"use client";
import { Mic, Square } from "lucide-react";

export default function MicButton({ isRecording, startOp, stopOp }: { isRecording: boolean; startOp: () => void; stopOp: () => void }) {
    return (
        <button onClick={isRecording ? stopOp : startOp} type="button"
            className={`w-9 h-9 rounded-xl flex items-center justify-center transition-all duration-200
                ${isRecording
                    ? "bg-red-500/20 border border-red-500/50 text-red-400 glow-pulse"
                    : "bg-gradient-to-br from-teal-500 to-emerald-500 text-white hover:scale-105 shadow-md shadow-teal-500/30"
                }`}
            title={isRecording ? "Stop recording" : "Start voice input"}>
            {isRecording
                ? <Square fill="currentColor" strokeWidth={0} className="w-3.5 h-3.5" />
                : <Mic className="w-4 h-4" />
            }
        </button>
    );
}
