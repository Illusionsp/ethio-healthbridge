"use client";

import { useState, useRef, useEffect } from "react";
import MicButton from "../components/MicButton";
import AudioPlayer from "../components/AudioPlayer";
import CameraUI from "../components/CameraUI";
import { useVoiceProcessor } from "../hooks/useVoiceProcessor";
import { api } from "../lib/api";
import { SendHorizontal, AlertTriangle } from "lucide-react";

const EmergencyTransportButton = () => {
    const [status, setStatus] = useState<"idle" | "booking" | "booked">("idle");

    return (
        <button
            type="button"
            className={`inline-flex items-center justify-center gap-2 px-4 py-2 rounded-full text-sm font-bold transition-all shadow-md active:scale-95 w-fit ${status === "booked"
                ? "bg-gradient-to-r from-green-600 to-green-800 text-white"
                : "bg-gradient-to-r from-red-600 to-red-800 hover:from-red-500 hover:to-red-700 text-white"
                }`}
            onClick={() => {
                if (status === "idle") {
                    setStatus("booking");
                    setTimeout(() => setStatus("booked"), 2500);
                }
            }}
            disabled={status !== "idle"}
        >
            {status === "idle" && "🚑 Request Emergency Transport (አምቡላንስ ጥራ)"}
            {status === "booking" && <span className="animate-pulse">🚑 Booking ride... (አምቡላንስ እየተጠራ ነው...)</span>}
            {status === "booked" && "✅ Ride Booked! (አምቡላንስ ተጠርቷል)"}
        </button>
    );
};

type Message = {
    id: string;
    role: "user" | "assistant";
    text: string;
    audioUrl?: string | null;
    isEmergency?: boolean;
    isTemporary?: boolean;
};

export default function Home() {
    const [messages, setMessages] = useState<Message[]>([]);
    const [isClient, setIsClient] = useState(false);

    // Initialize standard prompt if empty
    useEffect(() => {
        setIsClient(true);
        const saved = localStorage.getItem("ethio-chat-history");
        if (saved) {
            setMessages(JSON.parse(saved));
        } else {
            setMessages([{
                id: "system-1",
                role: "assistant",
                text: "ጤና ይስጥልኝ፣ የኢትዮ ሄልዝ-ብሪጅ (Ethio-HealthBridge) ረዳት ነኝ። በድምፅ ወይም በፅሁፍ የህክምና ጥያቄዎን ሊጠይቁኝ ይችላሉ። ወይንም የመድሃኒትዎን ምስል በማንሳት ማብራሪያ ማግኘት ይችላሉ።\n(Hello, I am the Ethio-HealthBridge assistant. You can ask medical questions via text or voice, or upload a medicine label for analysis.)"
            }]);
        }
    }, []);

    // Save to local storage on message change
    useEffect(() => {
        if (isClient && messages.length > 0) {
            // Filter out temporary messages before saving
            const persistable = messages.filter(m => !m.isTemporary);
            localStorage.setItem("ethio-chat-history", JSON.stringify(persistable));
        }
    }, [messages, isClient]);

    const [inputText, setInputText] = useState("");
    const [isRecording, setIsRecording] = useState(false);
    const [isProcessing, setIsProcessing] = useState(false);

    const messagesEndRef = useRef<HTMLDivElement>(null);
    const mediaRecorderRef = useRef<MediaRecorder | null>(null);
    const chunksRef = useRef<BlobPart[]>([]);

    const { processVoice } = useVoiceProcessor();

    // Scroll to bottom on new message
    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }, [messages]);

    const addMessage = (msg: Omit<Message, "id">) => {
        setMessages(prev => [...prev, { ...msg, id: Date.now().toString() + Math.random().toString() }]);
    };

    const handleTextSubmit = async (e?: React.FormEvent) => {
        e?.preventDefault();
        if (!inputText.trim() || isProcessing) return;

        const text = inputText;
        setInputText("");
        addMessage({ role: "user", text });
        setIsProcessing(true);

        try {
            const res = await api.post("/api/text-chat", { text });
            addMessage({
                role: "assistant",
                text: res.data.response_text,
                audioUrl: res.data.audio_url,
                isEmergency: res.data.emergency
            });
        } catch (err) {
            addMessage({ role: "assistant", text: "ይቅርታ፣ አሁን ላይ አውታረ መረብ አይሰራም። (Network Error)" });
        } finally {
            setIsProcessing(false);
        }
    };

    const startRecording = async () => {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            mediaRecorderRef.current = new MediaRecorder(stream);
            chunksRef.current = [];

            mediaRecorderRef.current.ondataavailable = (e) => {
                if (e.data.size > 0) chunksRef.current.push(e.data);
            };

            mediaRecorderRef.current.onstop = async () => {
                const blob = new Blob(chunksRef.current, { type: "audio/webm" });
                setIsProcessing(true);

                // Add a temporary "Processing Audio..." message
                const tempId = Date.now().toString();
                setMessages(prev => [...prev, { id: tempId, role: "user", text: "🎙️ የድምፅ መልእክት በመተርጎም ላይ... (Processing Amharic audio...)", isTemporary: true }]);

                try {
                    const result = await processVoice(blob);

                    // Replace temp message with actual transcription
                    setMessages(prev => prev.map(m => m.id === tempId ? { ...m, text: result.transcription, isTemporary: false } : m));

                    addMessage({
                        role: "assistant",
                        text: result.response_text,
                        audioUrl: result.audio_url,
                        isEmergency: result.emergency
                    });
                } catch (error) {
                    setMessages(prev => prev.map(m => m.id === tempId ? { ...m, text: "Audio processing failed.", isTemporary: false } : m));
                } finally {
                    setIsProcessing(false);
                }
            };

            mediaRecorderRef.current.start();
            setIsRecording(true);
        } catch (err) {
            console.error("Microphone denied", err);
        }
    };

    const stopRecording = () => {
        if (mediaRecorderRef.current && isRecording) {
            mediaRecorderRef.current.stop();
            setIsRecording(false);
            mediaRecorderRef.current.stream.getTracks().forEach(t => t.stop());
        }
    };

    const handleVisionResult = (resultText: string) => {
        if (resultText.startsWith("[System]:")) {
            addMessage({ role: "user", text: resultText });
        } else {
            addMessage({ role: "assistant", text: resultText });
        }
    };

    const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleTextSubmit();
        }
    };

    return (
        <main className="flex flex-col h-screen bg-[#2e1d15] text-[#f7eedf] font-sans selection:bg-amber-600/30 overflow-hidden">

            {/* Background elements - Ethereal Flag Colors & Coffee Tones */}
            <div className="fixed inset-0 z-0 overflow-hidden pointer-events-none opacity-40">
                <div className="absolute top-[-20%] left-[-10%] w-[50%] h-[50%] rounded-full bg-green-600/20 blur-[120px]" />
                <div className="absolute top-[20%] right-[-10%] w-[50%] h-[50%] rounded-full bg-yellow-500/20 blur-[150px]" />
                <div className="absolute bottom-[-10%] left-[20%] w-[60%] h-[60%] rounded-full bg-red-600/20 blur-[150px]" />
            </div>

            {/* Header */}
            <header className="flex-none p-4 md:px-8 border-b border-[#4d3224] bg-[#22140e]/90 backdrop-blur-md z-10 flex justify-between items-center shadow-md">
                <div className="flex items-center gap-3">
                    <div className="w-8 h-8 rounded-full bg-gradient-to-br from-green-500 via-yellow-400 to-red-500 shadow-lg" />
                    <h1 className="text-xl font-bold tracking-tight text-transparent bg-clip-text bg-gradient-to-r from-amber-200 to-amber-500 drop-shadow-sm">
                        Ethio-HealthBridge
                    </h1>
                </div>
                <div className="text-[10px] md:text-xs uppercase tracking-widest text-[#d4bca4] font-semibold border border-[#d4bca4]/30 px-3 py-1 rounded-full bg-[#3e2723]/50">
                    ምርጥ የጤና ረዳት
                </div>
            </header>

            {/* Chat History Area */}
            <div className="flex-1 overflow-y-auto p-4 md:p-8 space-y-6 scroll-smooth z-10 w-full mb-2">
                <div className="max-w-3xl mx-auto space-y-6 flex flex-col">
                    {messages.map((msg) => (
                        <div key={msg.id} className={`flex flex-col max-w-[85%] ${msg.role === "user" ? "self-end items-end" : "self-start items-start"}`}>
                            {/* Emergency Badge */}
                            {msg.isEmergency && (
                                <div className="mb-3 flex flex-col gap-2">
                                    <div className="inline-flex items-center gap-2 bg-red-700/80 border border-red-500 text-white px-3 py-2 rounded-full text-sm font-bold shadow-lg shadow-red-900/50 w-fit animate-pulse">
                                        <AlertTriangle className="w-5 h-5" />
                                        ድንገተኛ (RED FLAG DETECTED)
                                    </div>
                                    <EmergencyTransportButton />
                                </div>
                            )}

                            {/* Bubble */}
                            <div className={`px-5 py-4 rounded-3xl shadow-md flex flex-col gap-3 max-w-full ${msg.role === "user"
                                ? "bg-gradient-to-br from-[#10562e] to-[#0a351c] text-[#e8f5e9] border border-[#1b7b43] rounded-br-none"
                                : "bg-[#3e2723] text-[#f7eedf] border border-[#5d4037] rounded-bl-none border-l-4 border-l-yellow-500 w-fit"
                                } ${msg.isTemporary ? "animate-pulse italic opacity-80" : ""}`}>
                                <p className="text-[16px] md:text-lg leading-relaxed whitespace-pre-wrap font-serif tracking-wide break-words">{msg.text}</p>

                                {/* Audio Player Attachment (if any) */}
                                {msg.audioUrl && (
                                    <div className="w-full mt-1 shrink-0">
                                        <AudioPlayer audioUrl={msg.audioUrl} autoPlay={true} />
                                    </div>
                                )}
                            </div>
                        </div>
                    ))}

                    {/* Processing Indicator */}
                    {isProcessing && !messages.some(m => m.isTemporary) && (
                        <div className="self-start max-w-[85%] px-5 py-4 bg-[#3e2723] border border-[#5d4037] border-l-4 border-l-yellow-500 rounded-3xl rounded-bl-none opacity-90 shadow-md flex items-center gap-4">
                            <span className="text-[#f7eedf] text-[15px] animate-pulse italic font-serif">
                                AI እያሰበ ነው... (AI is thinking...)
                            </span>
                            <div className="flex gap-1.5 items-end h-5">
                                <div className="w-1.5 bg-green-500 rounded-full animate-[bounce_1s_infinite_0ms]" style={{ height: '60%' }} />
                                <div className="w-1.5 bg-yellow-400 rounded-full animate-[bounce_1s_infinite_150ms]" style={{ height: '100%' }} />
                                <div className="w-1.5 bg-red-500 rounded-full animate-[bounce_1s_infinite_300ms]" style={{ height: '80%' }} />
                            </div>
                        </div>
                    )}

                    <div ref={messagesEndRef} className="h-4" />
                </div>
            </div>

            {/* Input Composer Area */}
            <div className="flex-none p-4 pb-8 md:p-6 bg-gradient-to-t from-[#1b0f0b] via-[#22140e] to-[#2e1d15]/50 w-full z-20 border-t border-[#4d3224]/30">
                <div className="max-w-3xl mx-auto relative">
                    <form onSubmit={handleTextSubmit} className="flex relative bg-[#3e2723] border border-[#5d4037] rounded-[2rem] shadow-2xl focus-within:border-yellow-500 focus-within:ring-2 focus-within:ring-yellow-500/20 transition-all p-1.5">
                        <div className="flex items-end pl-2 pb-1.5">
                            <CameraUI onAnalysisResult={handleVisionResult} />
                        </div>

                        <textarea
                            value={inputText}
                            onChange={(e) => setInputText(e.target.value)}
                            onKeyDown={handleKeyDown}
                            placeholder="የህክምና ጥያቄዎን እዚህ ያስገቡ... (Type here)"
                            className="flex-1 bg-transparent border-none focus:outline-none resize-none px-4 py-4 max-h-[150px] min-h-[56px] text-[#f7eedf] placeholder:text-[#a1887f] font-serif"
                            rows={1}
                        />

                        <div className="flex items-end pr-1.5 pb-1.5 gap-2">
                            {inputText.trim() ? (
                                <button
                                    type="submit"
                                    disabled={isProcessing}
                                    className="p-3 bg-gradient-to-b from-green-600 to-green-700 hover:from-green-500 hover:to-green-600 text-white rounded-full transition-colors disabled:opacity-50 flex items-center justify-center h-[44px] w-[44px] shadow-md border border-green-500"
                                >
                                    <SendHorizontal className="w-5 h-5 absolute" style={{ marginLeft: '-2px' }} />
                                </button>
                            ) : (
                                <MicButton
                                    isRecording={isRecording}
                                    startOp={startRecording}
                                    stopOp={stopRecording}
                                />
                            )}
                        </div>
                    </form>
                    <div className="flex flex-col items-center justify-center gap-2 mt-3">
                        <div className="flex items-center justify-center gap-2">
                            <span className="w-2 h-2 rounded-full bg-green-500"></span>
                            <span className="w-2 h-2 rounded-full bg-yellow-400"></span>
                            <span className="w-2 h-2 rounded-full bg-red-500"></span>
                            <p className="text-xs text-[#a1887f] font-medium border-x border-[#5d4037] px-2 mx-1 tracking-wide">
                                የኢትዮጵያ ጤና ሚኒስቴር መረጃ አጠቃቀም (MoH Protocols)
                            </p>
                            <span className="w-2 h-2 rounded-full bg-red-500"></span>
                            <span className="w-2 h-2 rounded-full bg-yellow-400"></span>
                            <span className="w-2 h-2 rounded-full bg-green-500"></span>
                        </div>
                        <p className="text-[10px] text-[#8d6e63] font-light text-center max-w-lg mb-1">
                            ማሳሰቢያ፡ ይህ መተግበሪያ ለሙከራ ብቻ የተሰራ ነው። ለትክክለኛ የህክምና ክትትል እባክዎ በአቅራቢያዎ ወደሚገኝ ጤና ተቋም ይሂዱ።<br />
                            <span className="opacity-70">(Disclaimer: This app is a prototype. For real medical conditions, please visit a clinic/call 912.)</span>
                        </p>
                    </div>
                </div>
            </div>
        </main>
    );
}
