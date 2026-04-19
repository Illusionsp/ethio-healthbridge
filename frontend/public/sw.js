const CACHE_NAME = "ethio-healthbridge-v3";

// App shell files to cache for offline use
const STATIC_ASSETS = [
    "/",
    "/manifest.json",
];

// Common offline responses for when the backend is unreachable
const OFFLINE_RESPONSES = {
    "/api/text-chat": {
        response_text:
            "ይቅርታ፣ አሁን ኢንተርኔት አይሰራም። እባክዎ ኔትወርክ ሲኖር ይሞክሩ።\n" +
            "(Offline: No internet connection. Please try when connected.)\n\n" +
            "ድንገተኛ ሁኔታ ከሆነ: 912 ይደውሉ። (Emergency: Call 912)",
        audio_url: null,
        emergency: false,
    },
    "/api/voice-chat": {
        transcription: "",
        response_text:
            "ይቅርታ፣ አሁን ኢንተርኔት አይሰራም። እባክዎ ኔትወርክ ሲኖር ይሞክሩ።\n" +
            "(Offline: No internet connection. Please try when connected.)\n\n" +
            "ድንገተኛ ሁኔታ ከሆነ: 912 ይደውሉ። (Emergency: Call 912)",
        audio_url: null,
        emergency: false,
    },
};

self.addEventListener("install", (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME).then((cache) => cache.addAll(STATIC_ASSETS))
    );
    self.skipWaiting();
});

self.addEventListener("activate", (event) => {
    event.waitUntil(
        caches.keys().then((keys) =>
            Promise.all(keys.filter((k) => k !== CACHE_NAME).map((k) => caches.delete(k)))
        )
    );
    self.clients.claim();
});

self.addEventListener("fetch", (event) => {
    const url = new URL(event.request.url);

    // For API POST requests — return offline fallback if network fails
    if (event.request.method === "POST" && url.pathname in OFFLINE_RESPONSES) {
        event.respondWith(
            fetch(event.request).catch(() => {
                const body = JSON.stringify(OFFLINE_RESPONSES[url.pathname]);
                return new Response(body, {
                    status: 200,
                    headers: { "Content-Type": "application/json" },
                });
            })
        );
        return;
    }

    // For GET requests — cache-first for static assets, network-first for everything else
    if (event.request.method === "GET") {
        event.respondWith(
            caches.match(event.request).then((cached) => {
                if (cached) return cached;
                return fetch(event.request).then((response) => {
                    // Cache successful static responses
                    if (response.ok && url.origin === self.location.origin) {
                        const clone = response.clone();
                        caches.open(CACHE_NAME).then((cache) => cache.put(event.request, clone));
                    }
                    return response;
                }).catch(() => cached || new Response("Offline", { status: 503 }));
            })
        );
    }
});
