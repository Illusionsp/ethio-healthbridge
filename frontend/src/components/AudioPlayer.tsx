"use client";
import { useEffect, useRef, useState } from "react";
import { Play, Pause, Volume2, VolumeX } from "lucide-react";

export default function AudioPlayer({ audioUrl, autoPlay = false }: { audioUrl: string | null; autoPlay?: boolean }) {
    const audioRef = useRef<HTMLAudioElement | null>(null);
    const [isPlaying, setIsPlaying] = useState(false);
    const [progress, setProgress] = useState(0);
    const [duration, setDuration] = useState(0);
    const [muted, setMuted] = useState(false);

    useEffect(() => {
        if (!audioUrl) return;
        const base = audioUrl.startsWith("http") ? audioUrl : `http://localhost:8000${audioUrl}`;
        const src = `${base}?t=${Date.now()}`;
        const audio = new Audio(src);
        audioRef.current = audio;

        audio.onloadedmetadata = () => setDuration(audio.duration);
        audio.ontimeupdate = () => setProgress(audio.currentTime / (audio.duration || 1));
        audio.onended = () => { setIsPlaying(false); setProgress(0); };

        if (autoPlay) {
            audio.play().then(() => setIsPlaying(true)).catch(() => setIsPlaying(false));
        }
        return () => { audio.pause(); audio.src = ""; audioRef.current = null; };
    }, [audioUrl, autoPlay]);

    const toggle = () => {
        if (!audioRef.current) return;
        if (isPlaying) { audioRef.current.pause(); setIsPlaying(false); }
        else { audioRef.current.play(); setIsPlaying(true); }
    };

    const seek = (e: React.MouseEvent<HTMLDivElement>) => {
        if (!audioRef.current) return;
        const rect = e.currentTarget.getBoundingClientRect();
        const ratio = (e.clientX - rect.left) / rect.width;
        audioRef.current.currentTime = ratio * audioRef.current.duration;
    };

    const toggleMute = () => {
        if (!audioRef.current) return;
        audioRef.current.muted = !muted;
        setMuted(p => !p);
    };

    const fmt = (s: number) => `${Math.floor(s / 60)}:${String(Math.floor(s % 60)).padStart(2, "0")}`;

    if (!audioUrl) return null;

    return (
        <div className="flex items-center gap-3 bg-[var(--bg-card)] border border-[var(--border)] rounded-2xl px-3 py-2.5 w-full max-w-xs">
            <button onClick={toggle}
                className="w-8 h-8 rounded-full bg-gradient-to-br from-teal-500 to-emerald-500 flex items-center justify-center shrink-0 hover:scale-105 transition-transform shadow-md shadow-teal-500/30">
                {isPlaying ? <Pause className="w-3.5 h-3.5 text-white" /> : <Play className="w-3.5 h-3.5 text-white ml-0.5" />}
            </button>

            {/* Waveform bars when playing, progress bar when paused */}
            <div className="flex-1 flex flex-col gap-1">
                {isPlaying ? (
                    <div className="flex items-center gap-0.5 h-6">
                        {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12].map((i) => (
                            <div key={i} className="w-1 rounded-full bg-gradient-to-t from-teal-500 to-emerald-400"
                                style={{
                                    height: `${Math.random() * 16 + 4}px`,
                                    animation: `wave-${(i % 5) + 1} ${0.6 + (i % 4) * 0.15}s ease-in-out infinite`,
                                    animationDelay: `${i * 0.05}s`
                                }} />
                        ))}
                    </div>
                ) : (
                    <div className="h-1.5 bg-[var(--border)] rounded-full cursor-pointer overflow-hidden" onClick={seek}>
                        <div className="h-full bg-gradient-to-r from-teal-500 to-emerald-400 rounded-full transition-all"
                            style={{ width: `${progress * 100}%` }} />
                    </div>
                )}
                <div className="flex justify-between text-[10px] text-[var(--text-muted)]">
                    <span>{fmt(progress * duration)}</span>
                    <span>{fmt(duration)}</span>
                </div>
            </div>

            <button onClick={toggleMute} className="text-[var(--text-muted)] hover:text-[var(--accent-teal)] transition-colors">
                {muted ? <VolumeX className="w-3.5 h-3.5" /> : <Volume2 className="w-3.5 h-3.5" />}
            </button>
        </div>
    );
}
