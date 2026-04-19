"use client";
import { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { MessageSquare, History, User, Info, ChevronLeft, ChevronRight, Activity, MapPin, Baby } from "lucide-react";

const NAV = [
    { href: "/", icon: MessageSquare, label: "Chat", labelAm: "ውይይት" },
    { href: "/history", icon: History, label: "History", labelAm: "ታሪክ" },
    { href: "/profile", icon: User, label: "Profile", labelAm: "መገለጫ" },
    { href: "/about", icon: Info, label: "About", labelAm: "ስለ እኛ" },
];

export default function Sidebar() {
    const [collapsed, setCollapsed] = useState(false);
    const pathname = usePathname();

    return (
        <aside className={`relative flex flex-col glass-bright border-r border-[var(--border)] transition-all duration-300 z-20 ${collapsed ? "w-16" : "w-56"}`}>
            {/* Logo */}
            <div className={`flex items-center gap-3 px-4 py-5 border-b border-[var(--border)] ${collapsed ? "justify-center px-2" : ""}`}>
                <div className="w-8 h-8 rounded-xl bg-gradient-to-br from-teal-400 via-emerald-400 to-cyan-500 flex items-center justify-center shadow-lg shadow-teal-500/30 shrink-0">
                    <Activity className="w-4 h-4 text-white" />
                </div>
                {!collapsed && (
                    <div>
                        <p className="text-sm font-bold text-[var(--accent-teal)] leading-none">Ethio</p>
                        <p className="text-xs text-[var(--text-secondary)] leading-none mt-0.5">HealthBridge</p>
                    </div>
                )}
            </div>

            {/* Nav links */}
            <nav className="flex-1 py-4 space-y-1 px-2">
                {NAV.map(({ href, icon: Icon, label, labelAm }) => {
                    const active = pathname === href;
                    return (
                        <Link key={href} href={href}
                            className={`flex items-center gap-3 px-3 py-2.5 rounded-xl transition-all duration-200 group relative
                                ${active
                                    ? "bg-teal-500/15 text-[var(--accent-teal)] border border-teal-500/30"
                                    : "text-[var(--text-secondary)] hover:bg-white/5 hover:text-[var(--text-primary)]"
                                } ${collapsed ? "justify-center" : ""}`}
                        >
                            {active && <div className="absolute left-0 top-1/2 -translate-y-1/2 w-0.5 h-6 bg-[var(--accent-teal)] rounded-full" />}
                            <Icon className={`w-4.5 h-4.5 shrink-0 ${active ? "text-[var(--accent-teal)]" : ""}`} />
                            {!collapsed && (
                                <div>
                                    <p className="text-sm font-medium leading-none">{label}</p>
                                    <p className="text-[10px] opacity-60 mt-0.5">{labelAm}</p>
                                </div>
                            )}
                            {/* Tooltip when collapsed */}
                            {collapsed && (
                                <div className="absolute left-full ml-2 px-2 py-1 bg-[var(--bg-card)] border border-[var(--border)] rounded-lg text-xs text-[var(--text-primary)] whitespace-nowrap opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none z-50">
                                    {label}
                                </div>
                            )}
                        </Link>
                    );
                })}
            </nav>

            {/* Status dot */}
            {!collapsed && (
                <div className="px-4 py-3 border-t border-[var(--border)]">
                    <div className="flex items-center gap-2">
                        <div className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
                        <span className="text-xs text-[var(--text-muted)]">MoH RAG Active</span>
                    </div>
                </div>
            )}

            {/* Collapse toggle */}
            <button
                onClick={() => setCollapsed(p => !p)}
                className="absolute -right-3 top-20 w-6 h-6 rounded-full bg-[var(--bg-card)] border border-[var(--border)] flex items-center justify-center text-[var(--text-secondary)] hover:text-[var(--accent-teal)] hover:border-teal-500/50 transition-all z-30"
            >
                {collapsed ? <ChevronRight className="w-3 h-3" /> : <ChevronLeft className="w-3 h-3" />}
            </button>
        </aside>
    );
}
