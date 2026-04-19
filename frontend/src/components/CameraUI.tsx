"use client";

import { Camera } from "lucide-react";
import { useState, useRef } from "react";
import { api } from "../lib/api";

export default function CameraUI({ onAnalysisResult }: { onAnalysisResult: (text: string, audioUrl?: string) => void }) {
    const fileInputRef = useRef<HTMLInputElement>(null);
    const [isAnalyzing, setIsAnalyzing] = useState(false);

    const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        if (!file) return;

        setIsAnalyzing(true);
        const formData = new FormData();
        formData.append("image", file);

        // Notify parent that we started analyzing an image
        onAnalysisResult(`[System]: Uploading image ${file.name}...`);

        try {
            const res = await api.post("/api/vision-analyze", formData, {
                headers: { "Content-Type": "multipart/form-data" }
            });
            onAnalysisResult(res.data.analysis, res.data.audio_url);
        } catch (error) {
            onAnalysisResult("ይቅርታ፣ ችግር ተፈጥሯል። (Sorry, an error occurred analyzing the image.)");
        } finally {
            setIsAnalyzing(false);
        }
    };

    return (
        <>
            <input
                type="file"
                accept="image/*"
                className="hidden"
                ref={fileInputRef}
                onChange={handleFileSelect}
            />
            <button
                type="button"
                onClick={() => fileInputRef.current?.click()}
                disabled={isAnalyzing}
                className={`flex items-center justify-center p-3 rounded-full transition-all duration-300 ${isAnalyzing
                    ? 'text-[#a1887f] bg-[#5d4037]/50 cursor-not-allowed border border-[#5d4037]'
                    : 'text-[#d4bca4] bg-[#5d4037] hover:text-amber-200 hover:bg-[#6d4c41] border border-[#d4bca4]/30'
                    }`}
                title="የመድሃኒት ምስል ያስገቡ (Scan Medicine)"
            >
                {isAnalyzing ? (
                    <div className="w-5 h-5 rounded-full border-2 border-[#a1887f] border-t-[#d4bca4] animate-spin" />
                ) : (
                    <Camera className="w-5 h-5" />
                )}
            </button>
        </>
    );
}
