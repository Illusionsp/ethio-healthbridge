"use client";

import { useEffect, useRef, useState } from "react";
import { Play, Pause, Volume2 } from "lucide-react";

export default function AudioPlayer({ audioUrl, autoPlay = false }: { audioUrl: string | null, autoPlay?: boolean }) {
    const audioRef = useRef<HTMLAudioElement | null>(null);
    const [isPlaying, setIsPlaying] = useState(false);

    useEffect(() => {
        if (audioUrl) {
            // 1. Resolve the base URL
            const baseUrl = audioUrl.startsWith('http') ? audioUrl : `http://localhost:8000${audioUrl}`;
            
            // 2. THE FIX: Add a unique timestamp so the browser NEVER plays a cached file
            const urlPath = `${baseUrl}?t=${Date.now()}`;
            
            audioRef.current = new Audio(urlPath);

            audioRef.current.onended = () => {
                setIsPlaying(false);
                if (audioRef.current) audioRef.current.currentTime = 0; // Reset so it can be played again
            };

            if (autoPlay) {
                // 3. THE FIX: Only set isPlaying to true if the browser allows playback
                audioRef.current.play()
                    .then(() => setIsPlaying(true))
                    .catch(e => {
                        console.warn("Auto-playback blocked by browser:", e);
                        setIsPlaying(false);
                    });
            }
        }

        // Cleanup function to stop memory leaks
        return () => {
            if (audioRef.current) {
                audioRef.current.pause();
                audioRef.current.src = "";
                audioRef.current = null;
            }
        };
    }, [audioUrl, autoPlay]);

    const togglePlay = () => {
        if (!audioRef.current) return;
        if (isPlaying) {
            audioRef.current.pause();
        } else {
            // If it reached the end, start from zero
            if (audioRef.current.currentTime === audioRef.current.duration) {
                audioRef.current.currentTime = 0;
            }
            audioRef.current.play();
        }
        setIsPlaying(!isPlaying);
    };

    if (!audioUrl) return null;

    return (
        <div className="mt-2 flex items-center gap-3 bg-[#5d4037]/40 border border-[#8d6e63]/30 p-2 rounded-xl backdrop-blur-md w-full max-w-[250px] inline-flex shadow-inner">
            <button
                onClick={togglePlay}
                className="w-8 h-8 flex items-center justify-center bg-gradient-to-b from-yellow-500 to-yellow-600 text-[#3e2723] rounded-full hover:from-yellow-400 hover:to-yellow-500 transition-colors shadow-sm"
                title="Play Audio"
            >
                {isPlaying ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4 ml-0.5" />}
            </button>
            <div className="flex-1">
                <div className="h-1.5 w-full bg-[#3e2723] rounded-full overflow-hidden border border-[#2e1d15]/50">
                    <div className={`h-full bg-gradient-to-r from-green-500 via-yellow-400 to-red-500 transition-all duration-300 ${isPlaying ? 'w-full origin-left animate-pulse' : 'w-0'}`}></div>
                </div>
            </div>
            <Volume2 className="w-4 h-4 text-[#d4bca4] mr-2" />
        </div>
    );
}