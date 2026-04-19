"use client";
export default function AuroraBackground() {
    return (
        <div className="fixed inset-0 z-0 overflow-hidden pointer-events-none">
            <div className="aurora-1 absolute top-[-30%] left-[-20%] w-[70%] h-[70%] rounded-full bg-teal-500/10 blur-[120px]" />
            <div className="aurora-2 absolute top-[10%] right-[-25%] w-[65%] h-[65%] rounded-full bg-emerald-500/8 blur-[140px]" />
            <div className="aurora-3 absolute bottom-[-20%] left-[15%] w-[75%] h-[60%] rounded-full bg-blue-600/8 blur-[160px]" />
            <div className="aurora-1 absolute top-[40%] left-[40%] w-[40%] h-[40%] rounded-full bg-cyan-400/6 blur-[100px]" />
            {/* Grid overlay */}
            <div className="absolute inset-0 opacity-[0.03]"
                style={{
                    backgroundImage: `linear-gradient(rgba(0,212,170,0.5) 1px, transparent 1px),
                                      linear-gradient(90deg, rgba(0,212,170,0.5) 1px, transparent 1px)`,
                    backgroundSize: "60px 60px"
                }}
            />
        </div>
    );
}
