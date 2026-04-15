"use client";

import { Mic, Square } from "lucide-react";

export default function MicButton({ isRecording, startOp, stopOp }: { isRecording: boolean, startOp: () => void, stopOp: () => void }) {
    return (
        <button
            onClick={isRecording ? stopOp : startOp}
            type="button"
            className={`flex items-center justify-center p-3 rounded-full transition-all duration-300 ${isRecording
                    ? "bg-red-600 text-white hover:bg-red-700 animate-pulse shadow-[0_0_15px_rgba(220,38,38,0.5)] border border-red-500"
                    : "bg-gradient-to-b from-yellow-500 to-yellow-600 hover:from-yellow-400 hover:to-yellow-500 text-[#3e2723] shadow-md border border-yellow-400"
                }`}
            title="ድምፅ ይቅረጹ (Voice Record)"
        >
            {isRecording ? (
                <Square fill="currentColor" strokeWidth={0} className="w-5 h-5" />
            ) : (
                <Mic className="w-5 h-5" />
            )}
        </button>
    );
}
