"use client";
import Sidebar from "./Sidebar";
import AuroraBackground from "./AuroraBackground";

export default function AppShell({ children }: { children: React.ReactNode }) {
    return (
        <div className="flex h-screen bg-[var(--bg-primary)]" style={{ overflow: "hidden", position: "relative" }}>
            <AuroraBackground />
            <Sidebar />
            <main className="flex-1 overflow-hidden relative z-10">
                {children}
            </main>
        </div>
    );
}
