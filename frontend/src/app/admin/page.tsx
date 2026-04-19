"use client";

import { useEffect, useState } from "react";
import { AlertTriangle, Activity, ShieldAlert, Eye } from "lucide-react";
import { api } from "../../lib/api";

type HotspotData = Record<string, Record<string, number>>;

export default function AdminDashboard() {
    const [hotspots, setHotspots] = useState<HotspotData>({});
    const [loading, setLoading] = useState(true);
    const [isAuthenticated, setIsAuthenticated] = useState(false);
    const [passwordInput, setPasswordInput] = useState("");

    const fetchHotspots = async () => {
        try {
            const res = await api.get("/api/hotspots");
            setHotspots(res.data.data || {});
        } catch (error) {
            console.error("Failed to fetch hotspots:", error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchHotspots();
        // Refresh every 10 seconds
        const interval = setInterval(fetchHotspots, 10000);
        return () => clearInterval(interval);
    }, []);

    const getTotalSignals = (cityData: Record<string, number>) => {
        return Object.values(cityData).reduce((a, b) => a + b, 0);
    };

    const getOpacityMap = (count: number) => {
        if (count < 3) return "bg-green-900/30 border-green-500/50";
        if (count < 8) return "bg-yellow-900/40 border-yellow-500/60 shadow-[0_0_15px_rgba(234,179,8,0.15)]";
        return "bg-red-900/50 border-red-500 shadow-[0_0_30px_rgba(239,68,68,0.3)]";
    };

    const getAlertLevel = (count: number) => {
        if (count < 3) return { text: "LOW PRIORITY", icon: <Eye className="w-4 h-4 text-green-400" /> };
        if (count < 8) return { text: "ELEVATED RISK", icon: <AlertTriangle className="w-4 h-4 text-yellow-400" /> };
        return { text: "OUTBREAK ALARM", icon: <ShieldAlert className="w-4 h-4 text-red-500 animate-pulse" /> };
    };

    const getSystemWideTopSymptom = () => {
        const tally: Record<string, number> = {};
        let total = 0;
        Object.values(hotspots).forEach(cityData => {
            Object.entries(cityData).forEach(([sym, count]) => {
                tally[sym] = (tally[sym] || 0) + count;
                total += count;
            });
        });
        const sorted = Object.entries(tally).sort((a, b) => b[1] - a[1]);
        return {
            topSym: sorted.length > 0 ? sorted[0][0] : "None",
            topCount: sorted.length > 0 ? sorted[0][1] : 0,
            total: total || 1 // prevent division by zero in UI
        };
    };

    if (!isAuthenticated) {
        return (
            <div className="min-h-screen bg-[#1b0f0b] text-[#f7eedf] p-6 flex flex-col items-center justify-center font-sans">
                <div className="bg-[#2a170f] p-8 rounded-2xl border border-[#4d3224] w-full max-w-sm flex flex-col items-center text-center shadow-2xl">
                    <ShieldAlert className="w-12 h-12 text-red-500 mb-4 animate-pulse" />
                    <h1 className="text-xl font-bold mb-2 uppercase tracking-widest text-[#f7eedf]">Restricted Area</h1>
                    <p className="text-xs text-[#a1887f] mb-6 leading-relaxed">Ministry of Health Officials Only.<br />Enter administrator password.</p>
                    <form onSubmit={(e) => {
                        e.preventDefault();
                        if (passwordInput === "admin123") {
                            setIsAuthenticated(true);
                        } else {
                            alert("Incorrect Authorization Key");
                            setPasswordInput("");
                        }
                    }} className="w-full flex gap-2">
                        <input
                            type="password"
                            className="flex-1 bg-[#1b0f0b] border border-[#4d3224] rounded-lg px-4 py-2 focus:outline-none focus:border-red-500 focus:ring-1 focus:ring-red-500/50 text-sm transition-all"
                            placeholder="Password..."
                            value={passwordInput}
                            onChange={(e) => setPasswordInput(e.target.value)}
                            required
                        />
                        <button type="submit" className="bg-red-600 hover:bg-red-500 text-white font-bold px-4 py-2 rounded-lg text-sm transition-colors active:scale-95 shadow-[0_0_15px_rgba(220,38,38,0.4)] border border-red-500">
                            Unlock
                        </button>
                    </form>
                    <div className="mt-8 text-[10px] text-red-400 opacity-50 uppercase tracking-widest border border-red-500/30 px-3 py-1 rounded-full">(Hackathon Demo Pass: admin123)</div>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-[#1b0f0b] text-[#f7eedf] p-6 lg:p-12 font-sans selection:bg-red-500/30">
            <header className="mb-12 border-b border-[#4d3224] pb-6 flex flex-col md:flex-row md:justify-between md:items-end gap-6 justify-between">
                <div>
                    <div className="flex items-center gap-3 mb-2">
                        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-red-600 to-red-900 shadow-xl flex items-center justify-center border border-red-500/50">
                            <Activity className="text-white w-6 h-6 animate-pulse" />
                        </div>
                        <h1 className="text-3xl font-bold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-[#f7eedf] to-[#a1887f]">
                            Ministry of Health E.W.S
                        </h1>
                    </div>
                    <p className="text-[#a1887f] tracking-wide text-sm max-w-xl">
                        Early Warning System powered by AI. Real-time geographical symptom aggregation for predictive epidemic tracking.
                    </p>
                </div>

                <div className="flex items-center gap-2 bg-[#2a170f] px-4 py-2 rounded-lg border border-[#4d3224]">
                    <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
                    <span className="text-xs font-mono uppercase tracking-widest text-green-400">Live Telemetry active</span>
                </div>
            </header>

            {!loading && Object.keys(hotspots).length > 0 && (
                <div className="mb-10 grid grid-cols-1 md:grid-cols-3 gap-6">
                    {(() => {
                        const { topSym, topCount, total } = getSystemWideTopSymptom();
                        return (
                            <>
                                <div className="bg-[#2a170f] border border-[#4d3224] rounded-2xl p-6 relative overflow-hidden transition-all hover:border-[#5d4037]">
                                    <div className="absolute -right-6 -top-6 text-red-900/20">
                                        <Activity className="w-40 h-40" />
                                    </div>
                                    <p className="text-[10px] uppercase tracking-widest text-[#a1887f] font-semibold mb-1 relative z-10">Total Network Pings</p>
                                    <h2 className="text-4xl font-bold font-mono tracking-tighter text-[#f7eedf] relative z-10">{total}</h2>
                                    <p className="text-[10px] text-green-400 mt-2 flex items-center gap-1 relative z-10 font-bold tracking-widest"><span>↑</span> +12% vs last week</p>
                                </div>
                                <div className="bg-[#2a170f] border border-red-900 rounded-2xl p-6 relative overflow-hidden shadow-[0_0_20px_rgba(220,38,38,0.15)] col-span-1 md:col-span-2 flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
                                    <div>
                                        <p className="text-[10px] uppercase tracking-widest text-red-400 font-bold mb-1 flex items-center gap-2">
                                            <ShieldAlert className="w-3 h-3 animate-pulse" />
                                            #1 National Surge Indicator
                                        </p>
                                        <h2 className="text-4xl font-bold tracking-tighter text-white capitalize">{topSym}</h2>
                                    </div>
                                    <div className="bg-[#1b0f0b] border border-red-900/50 p-4 rounded-xl shadow-inner w-full md:w-auto">
                                        <p className="text-3xl font-mono text-red-400 font-bold">{Math.round((topCount / total) * 100)}%</p>
                                        <p className="text-[9px] uppercase tracking-widest text-[#a1887f]">of all recent signals</p>
                                    </div>
                                </div>
                            </>
                        );
                    })()}
                </div>
            )}

            {loading ? (
                <div className="flex justify-center items-center h-48">
                    <Activity className="w-10 h-10 text-red-500 animate-spin" />
                </div>
            ) : Object.keys(hotspots).length === 0 ? (
                <div className="text-center text-[#a1887f] mt-20">No telemetry data available yet. Connect endpoints.</div>
            ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                    {Object.entries(hotspots).sort((a, b) => getTotalSignals(b[1]) - getTotalSignals(a[1])).map(([subCity, symptoms]) => {
                        const total = getTotalSignals(symptoms);
                        const alertInfo = getAlertLevel(total);

                        return (
                            <div key={subCity} className={`p-6 rounded-2xl border backdrop-blur-md transition-all hover:scale-[1.02] cursor-default flex flex-col justify-between ${getOpacityMap(total)}`}>
                                <div>
                                    <div className="flex justify-between items-start mb-4">
                                        <h3 className="text-xl font-bold tracking-wide">{subCity}</h3>
                                        <div className="flex gap-1.5 items-center px-2 py-1 rounded-md bg-[#1b0f0b]/50 border border-black/20" title="Alert Status">
                                            {alertInfo.icon}
                                            <span className="text-[10px] uppercase tracking-widest font-bold opacity-80">{alertInfo.text}</span>
                                        </div>
                                    </div>

                                    <div className="space-y-3">
                                        <p className="text-xs uppercase tracking-widest text-[#a1887f] font-semibold border-b border-[#4d3224] pb-1">Detected Signals</p>
                                        {Object.entries(symptoms).sort((a, b) => b[1] - a[1]).map(([sym, count]) => {
                                            const percentage = Math.round((count / total) * 100);
                                            return (
                                                <div key={sym} className="flex flex-col gap-1.5 bg-[#2a170f]/40 p-3 rounded-xl border border-[#4d3224]/50 hover:bg-[#2a170f]/80 transition-colors">
                                                    <div className="flex justify-between items-center">
                                                        <span className="capitalize font-medium text-sm flex items-center gap-2">
                                                            {sym}
                                                            {percentage > 50 && <span className="text-[9px] bg-red-900/80 text-red-300 font-bold px-1.5 py-0.5 rounded-sm animate-pulse tracking-widest shadow-md">SURGE</span>}
                                                        </span>
                                                        <span className="text-xs font-mono tracking-widest text-[#d4bca4]">
                                                            {count}x <span className="opacity-50 ml-1">({percentage}%)</span>
                                                        </span>
                                                    </div>
                                                    <div className="w-full bg-[#1b0f0b] rounded-full h-1.5 overflow-hidden shadow-inner border border-[#3e2723]/50">
                                                        <div
                                                            className={`h-full rounded-full transition-all duration-1000 ease-out ${percentage > 50 ? 'bg-red-500 shadow-[0_0_8px_rgba(239,68,68,0.8)]' : percentage > 25 ? 'bg-yellow-500' : 'bg-green-500'}`}
                                                            style={{ width: `${percentage}%` }}
                                                        ></div>
                                                    </div>
                                                </div>
                                            );
                                        })}
                                    </div>
                                </div>
                                <div className="mt-6 pt-4 border-t border-black/10 flex justify-between items-center">
                                    <span className="text-[#a1887f] text-xs">Total Hits:</span>
                                    <span className="font-mono font-bold text-lg">{total}</span>
                                </div>
                            </div>
                        );
                    })}
                </div>
            )}
        </div>
    );
}
