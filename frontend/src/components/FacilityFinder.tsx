"use client";
import { useState, useEffect, useRef } from "react";
import { createPortal } from "react-dom";
import { MapPin, Loader2, X, ExternalLink, Navigation, LocateFixed } from "lucide-react";
import { api } from "../lib/api";

type Facility = {
    name: string; type: string;
    lat: number; lon: number;
    distance_km: number; maps_url: string;
};

const ADDIS = { lat: 9.0320, lon: 38.7469 };
const CACHE_KEY = "ehb-facilities-cache";
const CACHE_TTL = 5 * 60 * 1000; // 5 minutes

function getCache(): { data: Facility[]; label: string } | null {
    try {
        const raw = sessionStorage.getItem(CACHE_KEY);
        if (!raw) return null;
        const { data, label, ts } = JSON.parse(raw);
        if (Date.now() - ts > CACHE_TTL) return null;
        return { data, label };
    } catch { return null; }
}

function setCache(data: Facility[], label: string) {
    try {
        sessionStorage.setItem(CACHE_KEY, JSON.stringify({ data, label, ts: Date.now() }));
    } catch { }
}

const icons: Record<string, string> = {
    Hospital: "🏥", Clinic: "🏨", "Health Post": "🏠",
    Doctor: "👨‍⚕️", Pharmacy: "💊", "Health Facility": "🏥",
};

export default function FacilityFinder() {
    const [open, setOpen] = useState(false);
    const [loading, setLoading] = useState(false);
    const [facilities, setFacilities] = useState<Facility[]>([]);
    const [error, setError] = useState("");
    const [locLabel, setLocLabel] = useState("");
    const [mounted, setMounted] = useState(false);
    const fallbackRef = useRef<ReturnType<typeof setTimeout> | null>(null);

    useEffect(() => { setMounted(true); }, []);

    const search = async (lat: number, lon: number, label: string) => {
        if (fallbackRef.current) clearTimeout(fallbackRef.current);
        setLoading(true);
        setError("");
        setLocLabel(label);
        try {
            const res = await api.get("/api/nearby-facilities", {
                params: { lat, lon, radius: 5000 },
                timeout: 15000,
            });
            const data: Facility[] = res.data.facilities;
            if (data.length === 0) {
                setError("No facilities found within 5km.");
            } else {
                setFacilities(data);
                setCache(data, label);
            }
        } catch {
            setError("Could not load facilities. Check your connection.");
        } finally {
            setLoading(false);
        }
    };

    const openModal = () => {
        setOpen(true);
        setError("");

        // Serve from cache instantly if available
        const cached = getCache();
        if (cached) {
            setFacilities(cached.data);
            setLocLabel(cached.label + " (cached)");
            setLoading(false);
            return;
        }

        setFacilities([]);
        setLocLabel("Detecting location...");
        setLoading(true);

        if (!navigator.geolocation) {
            search(ADDIS.lat, ADDIS.lon, "Addis Ababa (default)");
            return;
        }

        // 4 second fallback — don't make user wait long
        fallbackRef.current = setTimeout(() => {
            search(ADDIS.lat, ADDIS.lon, "Addis Ababa (GPS slow)");
        }, 4000);

        navigator.geolocation.getCurrentPosition(
            (pos) => {
                if (fallbackRef.current) clearTimeout(fallbackRef.current);
                search(pos.coords.latitude, pos.coords.longitude, "Your location");
            },
            () => {
                if (fallbackRef.current) clearTimeout(fallbackRef.current);
                search(ADDIS.lat, ADDIS.lon, "Addis Ababa (location denied)");
            },
            { timeout: 3500, maximumAge: 120000, enableHighAccuracy: false }
        );
    };

    const modal = (
        <div
            style={{ position: "fixed", inset: 0, zIndex: 9999 }}
            className="flex items-end sm:items-center justify-center p-4 bg-black/70 backdrop-blur-sm"
            onClick={(e) => { if (e.target === e.currentTarget) setOpen(false); }}
        >
            <div
                style={{ background: "#041424", border: "1px solid #0e3a5c" }}
                className="w-full max-w-md rounded-3xl shadow-2xl overflow-hidden"
                onClick={(e) => e.stopPropagation()}
            >
                {/* Header */}
                <div style={{ borderBottom: "1px solid #0e3a5c" }} className="flex items-center justify-between px-5 py-4">
                    <div className="flex items-center gap-2">
                        <MapPin className="w-5 h-5 text-[var(--accent-teal)]" />
                        <div>
                            <p className="font-bold text-[var(--text-primary)] text-sm">Nearby Health Facilities</p>
                            {locLabel && (
                                <p className="text-[10px] text-[var(--text-muted)] flex items-center gap-1 mt-0.5">
                                    <LocateFixed className="w-2.5 h-2.5" /> {locLabel}
                                </p>
                            )}
                        </div>
                    </div>
                    <button onClick={() => setOpen(false)}
                        style={{ color: "#3d6b8a" }}
                        className="hover:text-white transition-colors p-1">
                        <X className="w-5 h-5" />
                    </button>
                </div>

                {/* Body */}
                <div className="p-4 overflow-y-auto space-y-2" style={{ maxHeight: "60vh" }}>
                    {loading && (
                        <div className="flex flex-col items-center py-10 gap-3">
                            <Loader2 className="w-8 h-8 animate-spin text-[var(--accent-teal)]" />
                            <p className="text-sm text-[var(--text-secondary)]">{locLabel}</p>
                            <p className="text-xs text-[var(--text-muted)]">Auto-falls back to Addis Ababa in 4s</p>
                        </div>
                    )}

                    {error && !loading && (
                        <div className="text-center py-6 space-y-3">
                            <p className="text-sm text-[var(--text-secondary)]">{error}</p>
                            <button onClick={() => search(ADDIS.lat, ADDIS.lon, "Addis Ababa")}
                                style={{ border: "1px solid rgba(0,212,170,0.3)", color: "#00d4aa" }}
                                className="text-xs px-4 py-2 rounded-full bg-teal-500/10 hover:bg-teal-500/20 transition-all">
                                Search near Addis Ababa
                            </button>
                        </div>
                    )}

                    {!loading && facilities.map((f, i) => (
                        <a key={i} href={f.maps_url} target="_blank" rel="noopener noreferrer"
                            style={{ background: "rgba(7,30,48,0.7)", border: "1px solid #0e3a5c", display: "flex" }}
                            className="items-start gap-3 p-3 rounded-2xl hover:border-teal-500/40 transition-all group">
                            <span className="text-xl mt-0.5 shrink-0">{icons[f.type] ?? "🏥"}</span>
                            <div className="flex-1 min-w-0">
                                <p className="font-semibold text-[var(--text-primary)] text-sm truncate">{f.name}</p>
                                <p className="text-xs text-[var(--text-muted)] mt-0.5">{f.type}</p>
                            </div>
                            <div className="flex flex-col items-end gap-1 shrink-0">
                                <span className="text-xs font-bold text-[var(--accent-teal)]">{f.distance_km} km</span>
                                <ExternalLink className="w-3 h-3 text-[var(--text-muted)] group-hover:text-[var(--accent-teal)]" />
                            </div>
                        </a>
                    ))}
                </div>

                {!loading && facilities.length > 0 && (
                    <div style={{ borderTop: "1px solid #0e3a5c" }}
                        className="px-5 py-3 flex items-center justify-between">
                        <div className="flex items-center gap-1.5 text-[10px] text-[var(--text-muted)]">
                            <Navigation className="w-3 h-3" /> Tap to open in OpenStreetMap
                        </div>
                        <button onClick={() => { sessionStorage.removeItem(CACHE_KEY); openModal(); }}
                            className="text-[10px] text-[var(--text-muted)] hover:text-teal-300 transition-colors underline">
                            Refresh
                        </button>
                    </div>
                )}
            </div>
        </div>
    );

    return (
        <>
            <button type="button" onClick={openModal}
                className="flex items-center gap-1.5 text-xs text-[var(--text-secondary)] border border-[var(--border)] px-2.5 py-1.5 rounded-full hover:border-teal-500/40 hover:text-teal-300 transition-all"
                title="Find nearest health facility">
                <MapPin className="w-3.5 h-3.5" />
                <span className="hidden sm:inline">ጤና ጣቢያ ፈልግ</span>
            </button>

            {/* Portal renders into #modal-root which is outside the entire app tree */}
            {mounted && open && createPortal(modal, document.getElementById("modal-root") ?? document.body)}
        </>
    );
}
