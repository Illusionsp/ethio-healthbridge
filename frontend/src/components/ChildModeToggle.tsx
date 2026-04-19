"use client";

import { Baby } from "lucide-react";

type Props = {
    isChildMode: boolean;
    onToggle: () => void;
};

export default function ChildModeToggle({ isChildMode, onToggle }: Props) {
    return (
        <button
            type="button"
            onClick={onToggle}
            title={isChildMode ? "Switch to Adult Mode" : "Switch to Child Health Mode"}
            className={`flex items-center gap-1.5 text-xs px-2.5 py-1.5 rounded-full border transition-all ${isChildMode
                    ? "bg-amber-500/20 border-amber-400/50 text-amber-300 font-semibold"
                    : "border-[var(--border)] text-[var(--text-secondary)] hover:border-teal-500/40 hover:text-teal-300"
                }`}
        >
            <Baby className="w-3.5 h-3.5" />
            <span className="hidden sm:inline">
                {isChildMode ? "የህፃን ሁነታ ✓" : "የህፃን ሁነታ"}
            </span>
        </button>
    );
}
