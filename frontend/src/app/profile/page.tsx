"use client";
import { useState, useEffect } from "react";
import AppShell from "../../components/AppShell";
import { useSymptomHistory } from "../../hooks/useSymptomHistory";
import { User, Edit3, Save, Baby, Globe, Bell, Shield, Activity, TrendingUp } from "lucide-react";

const LANGUAGES = ["Amharic (አማርኛ)", "Afaan Oromoo", "Tigrinya (ትግርኛ)"];

export default function ProfilePage() {
    const { history } = useSymptomHistory();
    const [editing, setEditing] = useState(false);
    const [profile, setProfile] = useState({ name: "", age: "", region: "", language: LANGUAGES[0], childMode: false, notifications: true });
    const [saved, setSaved] = useState(false);

    useEffect(() => {
        const p = localStorage.getItem("ethio-profile");
        if (p) setProfile(JSON.parse(p));
    }, []);

    const save = () => {
        localStorage.setItem("ethio-profile", JSON.stringify(profile));
        setEditing(false); setSaved(true);
        setTimeout(() => setSaved(false), 2000);
    };

    const recentSymptoms = [...new Set(history.slice(0, 10).map(e => e.symptoms.split(" ").slice(0, 3).join(" ")))].slice(0, 5);
    const totalSessions = history.length;
    const streak = Math.min(history.filter(e => Date.now() - e.timestamp < 7 * 86400000).length, 7);

    return (
        <AppShell>
            <div className="flex flex-col h-full overflow-hidden">
                <div className="flex-none px-6 py-4 glass-bright border-b border-[var(--border)]">
                    <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                            <User className="w-5 h-5 text-[var(--accent-teal)]" />
                            <h1 className="text-base font-bold text-[var(--text-primary)]">Profile</h1>
                            <span className="text-xs text-[var(--text-muted)]">መገለጫ</span>
                        </div>
                        <button onClick={() => editing ? save() : setEditing(true)}
                            className={`flex items-center gap-1.5 text-xs px-3 py-1.5 rounded-full border transition-all ${editing ? "bg-teal-500/20 border-teal-500/40 text-teal-300" : "border-[var(--border)] text-[var(--text-secondary)] hover:border-teal-500/40 hover:text-teal-300"}`}>
                            {editing ? <><Save className="w-3 h-3" /> Save</> : <><Edit3 className="w-3 h-3" /> Edit</>}
                        </button>
                    </div>
                    {saved && <p className="text-xs text-emerald-400 mt-1 fade-in">✓ Profile saved</p>}
                </div>

                <div className="flex-1 overflow-y-auto px-6 py-5 space-y-5">
                    {/* Avatar + name */}
                    <div className="glass rounded-2xl p-5 border border-[var(--border)] flex items-center gap-4">
                        <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-teal-500/30 to-emerald-500/20 border border-teal-500/30 flex items-center justify-center text-2xl">
                            {profile.name ? profile.name[0].toUpperCase() : "👤"}
                        </div>
                        <div className="flex-1">
                            {editing ? (
                                <input value={profile.name} onChange={e => setProfile(p => ({ ...p, name: e.target.value }))}
                                    placeholder="Your name"
                                    className="w-full bg-[var(--bg-card)] border border-[var(--border)] rounded-xl px-3 py-2 text-sm text-[var(--text-primary)] focus:outline-none focus:border-teal-500/50 mb-2" />
                            ) : (
                                <p className="text-base font-bold text-[var(--text-primary)]">{profile.name || "Anonymous User"}</p>
                            )}
                            <p className="text-xs text-[var(--text-muted)]">{profile.region || "Ethiopia"} · {profile.language.split(" ")[0]}</p>
                        </div>
                    </div>

                    {/* Stats */}
                    <div className="grid grid-cols-3 gap-3">
                        {[
                            { icon: Activity, label: "Sessions", value: totalSessions, color: "teal" },
                            { icon: TrendingUp, label: "This Week", value: streak, color: "emerald" },
                            { icon: Shield, label: "Safe Queries", value: history.filter(e => !e.response.includes("912")).length, color: "blue" },
                        ].map(({ icon: Icon, label, value, color }) => (
                            <div key={label} className="glass rounded-2xl p-3 text-center border border-[var(--border)]">
                                <Icon className={`w-4 h-4 mx-auto mb-1 text-${color}-400`} />
                                <p className={`text-xl font-bold text-${color}-400`}>{value}</p>
                                <p className="text-[10px] text-[var(--text-muted)]">{label}</p>
                            </div>
                        ))}
                    </div>

                    {/* Settings */}
                    <div className="glass rounded-2xl border border-[var(--border)] overflow-hidden">
                        <div className="px-4 py-3 border-b border-[var(--border)]">
                            <p className="text-xs font-semibold text-[var(--text-secondary)] uppercase tracking-wider">Preferences</p>
                        </div>
                        <div className="divide-y divide-[var(--border)]">
                            {/* Age */}
                            <div className="flex items-center justify-between px-4 py-3">
                                <div className="flex items-center gap-2">
                                    <User className="w-4 h-4 text-[var(--text-muted)]" />
                                    <span className="text-sm text-[var(--text-primary)]">Age</span>
                                </div>
                                {editing
                                    ? <input value={profile.age} onChange={e => setProfile(p => ({ ...p, age: e.target.value }))} placeholder="e.g. 32" className="w-20 bg-[var(--bg-card)] border border-[var(--border)] rounded-lg px-2 py-1 text-xs text-[var(--text-primary)] focus:outline-none text-right" />
                                    : <span className="text-sm text-[var(--text-secondary)]">{profile.age || "—"}</span>
                                }
                            </div>
                            {/* Region */}
                            <div className="flex items-center justify-between px-4 py-3">
                                <div className="flex items-center gap-2">
                                    <Globe className="w-4 h-4 text-[var(--text-muted)]" />
                                    <span className="text-sm text-[var(--text-primary)]">Region</span>
                                </div>
                                {editing
                                    ? <input value={profile.region} onChange={e => setProfile(p => ({ ...p, region: e.target.value }))} placeholder="e.g. Addis Ababa" className="w-36 bg-[var(--bg-card)] border border-[var(--border)] rounded-lg px-2 py-1 text-xs text-[var(--text-primary)] focus:outline-none text-right" />
                                    : <span className="text-sm text-[var(--text-secondary)]">{profile.region || "—"}</span>
                                }
                            </div>
                            {/* Language */}
                            <div className="flex items-center justify-between px-4 py-3">
                                <div className="flex items-center gap-2">
                                    <Globe className="w-4 h-4 text-[var(--text-muted)]" />
                                    <span className="text-sm text-[var(--text-primary)]">Language</span>
                                </div>
                                {editing
                                    ? <select value={profile.language} onChange={e => setProfile(p => ({ ...p, language: e.target.value }))} className="bg-[var(--bg-card)] border border-[var(--border)] rounded-lg px-2 py-1 text-xs text-[var(--text-primary)] focus:outline-none">
                                        {LANGUAGES.map(l => <option key={l}>{l}</option>)}
                                    </select>
                                    : <span className="text-sm text-[var(--text-secondary)]">{profile.language}</span>
                                }
                            </div>
                            {/* Child mode */}
                            <div className="flex items-center justify-between px-4 py-3">
                                <div className="flex items-center gap-2">
                                    <Baby className="w-4 h-4 text-[var(--text-muted)]" />
                                    <div>
                                        <p className="text-sm text-[var(--text-primary)]">Child Health Mode</p>
                                        <p className="text-[10px] text-[var(--text-muted)]">Pediatric guidance by default</p>
                                    </div>
                                </div>
                                <button onClick={() => editing && setProfile(p => ({ ...p, childMode: !p.childMode }))}
                                    className={`w-10 h-5 rounded-full transition-all relative ${profile.childMode ? "bg-amber-500" : "bg-[var(--border)]"}`}>
                                    <div className={`absolute top-0.5 w-4 h-4 rounded-full bg-white transition-all ${profile.childMode ? "left-5" : "left-0.5"}`} />
                                </button>
                            </div>
                        </div>
                    </div>

                    {/* Recent symptoms */}
                    {recentSymptoms.length > 0 && (
                        <div className="glass rounded-2xl border border-[var(--border)] p-4">
                            <p className="text-xs font-semibold text-[var(--text-secondary)] uppercase tracking-wider mb-3">Recent Symptoms</p>
                            <div className="flex flex-wrap gap-2">
                                {recentSymptoms.map((s, i) => (
                                    <span key={i} className="text-xs px-2.5 py-1 rounded-full bg-teal-500/10 border border-teal-500/20 text-teal-300">{s}</span>
                                ))}
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </AppShell>
    );
}
