/** @type {import('next').NextConfig} */
const nextConfig = {
    // Allow the service worker to be served from the root
    async headers() {
        return [
            {
                source: "/sw.js",
                headers: [
                    { key: "Cache-Control", value: "no-cache, no-store, must-revalidate" },
                    { key: "Content-Type", value: "application/javascript" },
                ],
            },
        ];
    },
};

module.exports = nextConfig;
