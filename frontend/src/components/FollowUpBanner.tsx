"use client";

import { Clock, X, RefreshCw } from "lucide-react";
import { SymptomEntry } from "../hooks/useSymptomHistory";

type Props = {
    entry: SymptomEntry;
    onFollowUp: (text: string) => void;
    onDismiss: () => void;
};

function timeAgo(timestamp: number): string {
    const hours = Math.floor((Date.now() - timestamp) / (1000 * 60 * 60));
    if (hours < 1) return "ከደቂቃዎች በፊት (minutes ago)";
    if (hours < 24) return `ከ${hours} ሰዓት በፊት (${hours}h ago)`;
    const days = Math.floor(hours / 24);
    return `ከ${days} ቀን በፊት (${days}d ago)`;
}

export default function FollowUpBanner({ entry, onFollowUp, onDismiss }: Props) {
    const preview = entry.symptoms.length > 60
        ? entry.symptoms.slice(0, 60) + "..."
        : entry.symptoms;

    const followUpText = `ትናንት "${preview}" ብዬ ጠይቄ ነበር። አሁን ሁኔታዬ እንዴት ነው? (Follow-up on previous symptoms: ${preview})`;

    return (
        <div className="mx-auto max-w-3xl px-4 pt-3">
            <div className="flex items-start gap-3 glass border border-teal-500/20 rounded-2xl px-4 py-3 shadow-md">
                <Clock className="w-4 h-4 text-[var(--accent-teal)] mt-0.5 shrink-0" />
                <div className="flex-1 min-w-0">
                    <p className="text-xs text-teal-300 font-semibold mb-0.5">
                        Previous consultation · {timeAgo(entry.timestamp)}
                    </p>
                    <p className="text-xs text-[var(--text-secondary)] truncate">{preview}</p>
                </div>
                <div className="flex items-center gap-2 shrink-0">
                    <button type="button" onClick={() => onFollowUp(followUpText)}
                        className="flex items-center gap-1 text-xs bg-teal-500/15 hover:bg-teal-500/25 text-teal-300 border border-teal-500/30 px-2.5 py-1 rounded-full transition-all">
                        <RefreshCw className="w-3 h-3" /> Follow-up
                    </button>
                    <button type="button" onClick={onDismiss} className="text-[var(--text-muted)] hover:text-[var(--text-secondary)] transition-colors">
                        <X className="w-4 h-4" />
                    </button>
                </div>
            </div>
        </div>
    );
}
