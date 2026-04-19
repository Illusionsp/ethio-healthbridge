"use client";
import { useState, useEffect } from "react";
import AppShell from "../../components/AppShell";
import { useSymptomHistory, SymptomEntry } from "../../hooks/useSymptomHistory";
import { History, Search, Trash2, ChevronDown, ChevronUp, Clock, MessageSquare, AlertTriangle } from "lucide-react";

function timeAgo(ts: number) {
    const diff = Date.now() - ts;
    const m = Math.floor(diff / 60000);
    const h = Math.floor(diff / 3600000);
    const d = Math.floor(diff / 86400000);
    if (m < 1) return "Just now";
    if (m < 60) return `${m}m ago`;
    if (h < 24) return `${h}h ago`;
    return `${d}d ago`;
}

function HistoryCard({ entry, index }: { entry: SymptomEntry; index: number }) {
    const [expanded, setExpanded] = useState(false);
    const isRecent = Date.now() - entry.timestamp < 3600000;

    return (
        <div className="glass rounded-2xl overflow-hidden border border-[var(--border)] hover:border-teal-500/30 transition-all slide-up"
            style={{ animationDelay: `${index * 60}ms` }}>
            <div className="flex items-start gap-3 p-4 cursor-pointer" onClick={() => setExpanded(p => !p)}>
                <div className="w-9 h-9 rounded-xl bg-teal-500/10 border border-teal-500/20 flex items-center justify-center shrink-0 mt-0.5">
                    <MessageSquare className="w-4 h-4 text-[var(--accent-teal)]" />
                </div>
                <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                        {isRecent && <span className="text-[10px] px-1.5 py-0.5 rounded-full bg-teal-500/15 text-teal-400 border border-teal-500/20">Recent</span>}
                        <span className="text-[10px] text-[var(--text-muted)] flex items-center gap-1">
                            <Clock className="w-3 h-3" />{timeAgo(entry.timestamp)}
                        </span>
                        <span className="text-[10px] text-[var(--text-muted)]">· {entry.language}</span>
                    </div>
                    <p className="text-sm text-[var(--text-primary)] font-medium truncate">{entry.symptoms}</p>
                    {!expanded && (
                        <p className="text-xs text-[var(--text-secondary)] mt-1 line-clamp-2 opacity-70">{entry.response}</p>
                    )}
                </div>
                <button className="text-[var(--text-muted)] hover:text-[var(--accent-teal)] transition-colors shrink-0">
                    {expanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                </button>
            </div>

            {expanded && (
                <div className="px-4 pb-4 border-t border-[var(--border)] pt-3 space-y-3 fade-in">
                    <div>
                        <p className="text-[10px] text-[var(--text-muted)] uppercase tracking-wider mb-1.5">Your Symptoms</p>
                        <p className="text-sm text-[var(--text-primary)] bg-teal-500/5 border border-teal-500/15 rounded-xl px-3 py-2">{entry.symptoms}</p>
                    </div>
                    <div>
                        <p className="text-[10px] text-[var(--text-muted)] uppercase tracking-wider mb-1.5">AI Response</p>
                        <p className="text-sm text-[var(--text-secondary)] bg-[var(--bg-card)] border border-[var(--border)] rounded-xl px-3 py-2 whitespace-pre-wrap leading-relaxed">{entry.response}</p>
                    </div>
                    <p className="text-[10px] text-[var(--text-muted)]">
                        {new Date(entry.timestamp).toLocaleString()}
                    </p>
                </div>
            )}
        </div>
    );
}

export default function HistoryPage() {
    const { history, clearHistory } = useSymptomHistory();
    const [search, setSearch] = useState("");
    const [isClient, setIsClient] = useState(false);
    useEffect(() => setIsClient(true), []);

    const filtered = history.filter(e =>
        e.symptoms.toLowerCase().includes(search.toLowerCase()) ||
        e.response.toLowerCase().includes(search.toLowerCase())
    );

    const stats = {
        total: history.length,
        today: history.filter(e => Date.now() - e.timestamp < 86400000).length,
        languages: [...new Set(history.map(e => e.language))].length,
    };

    return (
        <AppShell>
            <div className="flex flex-col h-full overflow-hidden">
                {/* Header */}
                <div className="flex-none px-6 py-4 glass-bright border-b border-[var(--border)]">
                    <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                            <History className="w-5 h-5 text-[var(--accent-teal)]" />
                            <h1 className="text-base font-bold text-[var(--text-primary)]">Symptom History</h1>
                            <span className="text-xs text-[var(--text-muted)]">ታሪክ</span>
                        </div>
                        {history.length > 0 && (
                            <button onClick={clearHistory}
                                className="flex items-center gap-1.5 text-xs text-red-400 hover:text-red-300 border border-red-500/30 hover:border-red-400/50 px-3 py-1.5 rounded-full transition-all">
                                <Trash2 className="w-3 h-3" /> Clear All
                            </button>
                        )}
                    </div>
                </div>

                <div className="flex-1 overflow-y-auto px-6 py-5 space-y-5">
                    {/* Stats */}
                    {isClient && (
                        <div className="grid grid-cols-3 gap-3">
                            {[
                                { label: "Total Sessions", value: stats.total, sub: "ጠቅላላ" },
                                { label: "Today", value: stats.today, sub: "ዛሬ" },
                                { label: "Languages", value: stats.languages, sub: "ቋንቋዎች" },
                            ].map(s => (
                                <div key={s.label} className="glass rounded-2xl p-4 text-center border border-[var(--border)]">
                                    <p className="text-2xl font-bold text-[var(--accent-teal)]">{s.value}</p>
                                    <p className="text-xs text-[var(--text-primary)] mt-0.5">{s.label}</p>
                                    <p className="text-[10px] text-[var(--text-muted)]">{s.sub}</p>
                                </div>
                            ))}
                        </div>
                    )}

                    {/* Search */}
                    {history.length > 0 && (
                        <div className="relative">
                            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[var(--text-muted)]" />
                            <input value={search} onChange={e => setSearch(e.target.value)}
                                placeholder="Search history..."
                                className="w-full glass border border-[var(--border)] rounded-xl pl-9 pr-4 py-2.5 text-sm text-[var(--text-primary)] placeholder:text-[var(--text-muted)] focus:outline-none focus:border-teal-500/50 transition-all" />
                        </div>
                    )}

                    {/* List */}
                    {!isClient ? (
                        <div className="space-y-3">
                            {[1, 2, 3].map(i => <div key={i} className="h-20 rounded-2xl shimmer" />)}
                        </div>
                    ) : filtered.length === 0 ? (
                        <div className="flex flex-col items-center justify-center py-20 gap-4 text-center">
                            <div className="w-16 h-16 rounded-2xl bg-[var(--bg-card)] border border-[var(--border)] flex items-center justify-center">
                                <History className="w-7 h-7 text-[var(--text-muted)]" />
                            </div>
                            <div>
                                <p className="text-sm font-medium text-[var(--text-secondary)]">
                                    {search ? "No results found" : "No history yet"}
                                </p>
                                <p className="text-xs text-[var(--text-muted)] mt-1">
                                    {search ? "Try a different search term" : "Start a chat to see your symptom history here"}
                                </p>
                            </div>
                        </div>
                    ) : (
                        <div className="space-y-3">
                            {filtered.map((e, i) => <HistoryCard key={e.id} entry={e} index={i} />)}
                        </div>
                    )}
                </div>
            </div>
        </AppShell>
    );
}
