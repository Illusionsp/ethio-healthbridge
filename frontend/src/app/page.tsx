"use client";
import { useState, useRef, useEffect, useCallback } from "react";
import AppShell from "../components/AppShell";
import MicButton from "../components/MicButton";
import AudioPlayer from "../components/AudioPlayer";
import CameraUI from "../components/CameraUI";
import FacilityFinder from "../components/FacilityFinder";
import ChildModeToggle from "../components/ChildModeToggle";
import FollowUpBanner from "../components/FollowUpBanner";
import { useVoiceProcessor } from "../hooks/useVoiceProcessor";
import { useSymptomHistory } from "../hooks/useSymptomHistory";
import { api } from "../lib/api";
import { SendHorizontal, AlertTriangle, Phone, Trash2, Wifi, WifiOff, Sparkles } from "lucide-react";

type Message = {
    id: string; role: "user" | "assistant";
    text: string; audioUrl?: string | null;
    isEmergency?: boolean; isTemporary?: boolean; timestamp?: number;
};

const WELCOME: Message = {
    id: "welcome", role: "assistant", timestamp: Date.now(),
    text: "ጤና ይስጥልኝ! እኔ Ethio-HealthBridge ነኝ — የኢትዮጵያ ጤና ሚኒስቴር መመሪያዎች ላይ የተመሰረተ AI ረዳት።\n\nAfaan Oromoo: Baga nagaan dhuftan!\n\nTigrinya: ሰላም! ብድምጺ ወይ ብጽሑፍ ሕማምካ ንገረኒ።\n\n(Speak or type in Amharic, Afaan Oromoo, or Tigrinya)"
};

function TypingText({ text }: { text: string }) {
    const [shown, setShown] = useState("");
    const [done, setDone] = useState(false);
    useEffect(() => {
        setShown(""); setDone(false);
        let i = 0;
        const id = setInterval(() => { i++; setShown(text.slice(0, i)); if (i >= text.length) { clearInterval(id); setDone(true); } }, 14);
        return () => clearInterval(id);
    }, [text]);
    return <span className={!done ? "typing-cursor" : ""}>{shown}</span>;
}

function EmergencyCard() {
    const [status, setStatus] = useState<"idle" | "booking" | "booked">("idle");
    return (
        <div className="mt-2 p-3 rounded-xl bg-red-950/40 border border-red-500/40 space-y-2">
            <div className="flex items-center gap-2 text-red-400 font-bold text-xs">
                <AlertTriangle className="w-3.5 h-3.5 animate-pulse" /> RED FLAG DETECTED
            </div>
            <div className="flex gap-2 flex-wrap">
                <a href="tel:912" className="flex items-center gap-1 px-3 py-1.5 bg-red-600 hover:bg-red-500 text-white text-xs font-bold rounded-full transition-colors">
                    <Phone className="w-3 h-3" /> Call 912
                </a>
                <button onClick={() => { if (status === "idle") { setStatus("booking"); setTimeout(() => setStatus("booked"), 2500); } }}
                    disabled={status !== "idle"}
                    className={`px-3 py-1.5 text-xs font-bold rounded-full transition-all ${status === "booked" ? "bg-emerald-600 text-white" : "bg-red-700 hover:bg-red-600 text-white"}`}>
                    {status === "idle" && "🚑 አምቡላንስ ጥራ"}{status === "booking" && <span className="animate-pulse">Booking...</span>}{status === "booked" && "✅ Booked!"}
                </button>
            </div>
        </div>
    );
}

export default function ChatPage() {
    const [messages, setMessages] = useState<Message[]>([]);
    const [isClient, setIsClient] = useState(false);
    const [inputText, setInputText] = useState("");
    const [isRecording, setIsRecording] = useState(false);
    const [isProcessing, setIsProcessing] = useState(false);
    const [isChildMode, setIsChildMode] = useState(false);
    const [isOnline, setIsOnline] = useState(true);
    const [showFollowUp, setShowFollowUp] = useState(true);
    const [newIds, setNewIds] = useState<Set<string>>(new Set());
    const endRef = useRef<HTMLDivElement>(null);
    const mediaRef = useRef<MediaRecorder | null>(null);
    const chunksRef = useRef<BlobPart[]>([]);
    const { processVoice } = useVoiceProcessor();
    const { addEntry, getRecentEntry } = useSymptomHistory();

    useEffect(() => {
        setIsClient(true);
        if ("serviceWorker" in navigator) navigator.serviceWorker.register("/sw.js").catch(() => { });
        const on = () => setIsOnline(true), off = () => setIsOnline(false);
        window.addEventListener("online", on); window.addEventListener("offline", off);
        setIsOnline(navigator.onLine);
        const saved = localStorage.getItem("ethio-chat-history");
        setMessages(saved ? JSON.parse(saved) : [WELCOME]);
        return () => { window.removeEventListener("online", on); window.removeEventListener("offline", off); };
    }, []);

    useEffect(() => {
        if (isClient && messages.length > 0)
            localStorage.setItem("ethio-chat-history", JSON.stringify(messages.filter(m => !m.isTemporary)));
    }, [messages, isClient]);

    useEffect(() => { endRef.current?.scrollIntoView({ behavior: "smooth" }); }, [messages]);

    const addMsg = useCallback((msg: Omit<Message, "id">) => {
        const id = Date.now().toString() + Math.random();
        setMessages(p => [...p, { ...msg, id, timestamp: Date.now() }]);
        setNewIds(p => new Set(p).add(id));
        setTimeout(() => setNewIds(p => { const n = new Set(p); n.delete(id); return n; }), 800);
    }, []);

    const submit = async (e?: React.FormEvent, override?: string) => {
        e?.preventDefault();
        const text = override ?? inputText;
        if (!text.trim() || isProcessing) return;
        setInputText("");
        addMsg({ role: "user", text });
        setIsProcessing(true);
        try {
            const res = await api.post("/api/text-chat", { text, mode: isChildMode ? "child" : "adult" });
            const { response_text, audio_url, emergency } = res.data;
            addMsg({ role: "assistant", text: response_text, audioUrl: audio_url, isEmergency: emergency });
            addEntry(text, response_text);
        } catch { addMsg({ role: "assistant", text: "ይቅርታ፣ አውታረ መረብ አይሰራም። (Network Error)" }); }
        finally { setIsProcessing(false); }
    };

    const startRec = async () => {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            mediaRef.current = new MediaRecorder(stream);
            chunksRef.current = [];
            mediaRef.current.ondataavailable = e => { if (e.data.size > 0) chunksRef.current.push(e.data); };
            mediaRef.current.onstop = async () => {
                const blob = new Blob(chunksRef.current, { type: "audio/webm" });
                setIsProcessing(true);
                const tempId = Date.now().toString();
                setMessages(p => [...p, { id: tempId, role: "user", text: "🎙️ Processing audio...", isTemporary: true, timestamp: Date.now() }]);
                try {
                    const r = await processVoice(blob, isChildMode ? "child" : "adult");
                    setMessages(p => p.map(m => m.id === tempId ? { ...m, text: r.transcription, isTemporary: false } : m));
                    addMsg({ role: "assistant", text: r.response_text, audioUrl: r.audio_url, isEmergency: r.emergency });
                    addEntry(r.transcription, r.response_text);
                } catch { setMessages(p => p.map(m => m.id === tempId ? { ...m, text: "Audio processing failed.", isTemporary: false } : m)); }
                finally { setIsProcessing(false); }
            };
            mediaRef.current.start(); setIsRecording(true);
        } catch (e) { console.error("Mic denied", e); }
    };

    const stopRec = () => {
        if (mediaRef.current && isRecording) {
            mediaRef.current.stop(); setIsRecording(false);
            mediaRef.current.stream.getTracks().forEach(t => t.stop());
        }
    };

    const recentEntry = isClient ? getRecentEntry() : null;

    return (
        <AppShell>
            <div className="flex flex-col h-full">
                {/* Top bar */}
                <div className="flex-none flex items-center justify-between px-5 py-3 glass-bright border-b border-[var(--border)]">
                    <div className="flex items-center gap-2">
                        <Sparkles className="w-4 h-4 text-[var(--accent-teal)]" />
                        <span className="text-sm font-semibold text-[var(--text-primary)]">AI Health Chat</span>
                        {isChildMode && <span className="text-xs px-2 py-0.5 rounded-full bg-amber-500/20 text-amber-300 border border-amber-500/30">👶 Child Mode</span>}
                    </div>
                    <div className="flex items-center gap-2">
                        {!isOnline
                            ? <div className="flex items-center gap-1 text-xs text-orange-400 border border-orange-400/30 px-2 py-1 rounded-full bg-orange-900/20"><WifiOff className="w-3 h-3" /><span className="hidden sm:inline">Offline</span></div>
                            : <div className="hidden sm:flex items-center gap-1 text-xs text-emerald-400/70 border border-emerald-400/20 px-2 py-1 rounded-full"><Wifi className="w-3 h-3" /></div>
                        }
                        <ChildModeToggle isChildMode={isChildMode} onToggle={() => setIsChildMode(p => !p)} />
                        <FacilityFinder />
                        <button onClick={() => { setMessages([WELCOME]); localStorage.removeItem("ethio-chat-history"); }} title="Clear chat"
                            className="p-1.5 rounded-lg text-[var(--text-muted)] hover:text-red-400 hover:bg-red-500/10 transition-all">
                            <Trash2 className="w-4 h-4" />
                        </button>
                    </div>
                </div>

                {isClient && recentEntry && showFollowUp && (
                    <FollowUpBanner entry={recentEntry}
                        onFollowUp={t => { setShowFollowUp(false); submit(undefined, t); }}
                        onDismiss={() => setShowFollowUp(false)} />
                )}

                {/* Messages */}
                <div className="flex-1 overflow-y-auto px-4 py-5">
                    <div className="max-w-3xl mx-auto flex flex-col gap-4">
                        {messages.map(msg => (
                            <div key={msg.id} className={`flex flex-col max-w-[82%] slide-up ${msg.role === "user" ? "self-end items-end" : "self-start items-start"}`}>
                                <span className="text-[10px] text-[var(--text-muted)] mb-1 px-1">
                                    {msg.role === "user" ? "You" : "Ethio-HealthBridge AI"}
                                    {msg.timestamp && ` · ${new Date(msg.timestamp).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}`}
                                </span>
                                <div className={`rounded-2xl px-4 py-3 shadow-lg flex flex-col gap-2 max-w-full
                  ${msg.role === "user"
                                        ? "bg-gradient-to-br from-teal-600/25 to-emerald-700/15 border border-teal-500/25 rounded-br-sm"
                                        : "glass border-l-2 border-l-[var(--accent-teal)] rounded-bl-sm"
                                    } ${msg.isTemporary ? "animate-pulse opacity-60 italic" : ""}`}>
                                    <p className="text-sm leading-relaxed whitespace-pre-wrap break-words text-[var(--text-primary)]">
                                        {msg.role === "assistant" && newIds.has(msg.id) && !msg.isTemporary
                                            ? <TypingText text={msg.text} />
                                            : msg.text}
                                    </p>
                                    {msg.audioUrl && <AudioPlayer audioUrl={msg.audioUrl} autoPlay={newIds.has(msg.id)} />}
                                    {msg.isEmergency && <EmergencyCard />}
                                </div>
                            </div>
                        ))}

                        {isProcessing && !messages.some(m => m.isTemporary) && (
                            <div className="self-start glass border-l-2 border-l-[var(--accent-teal)] rounded-2xl rounded-bl-sm px-4 py-3 flex items-center gap-3 slide-up">
                                {[0, 150, 300].map(d => (
                                    <div key={d} className="w-1.5 h-1.5 rounded-full bg-[var(--accent-teal)] animate-bounce" style={{ animationDelay: `${d}ms` }} />
                                ))}
                                <span className="text-xs text-[var(--text-secondary)] italic">AI is thinking...</span>
                            </div>
                        )}
                        <div ref={endRef} className="h-2" />
                    </div>
                </div>

                {/* Input */}
                <div className="flex-none px-4 pb-5 pt-3 glass-bright border-t border-[var(--border)]">
                    <div className="max-w-3xl mx-auto">
                        <form onSubmit={submit}
                            className="flex items-end gap-2 glass border border-[var(--border)] rounded-2xl p-2 focus-within:border-teal-500/50 focus-within:shadow-[0_0_20px_rgba(0,212,170,0.08)] transition-all">
                            <CameraUI onAnalysisResult={t => t.startsWith("[System]:") ? addMsg({ role: "user", text: t }) : addMsg({ role: "assistant", text: t })} />
                            <textarea value={inputText} onChange={e => setInputText(e.target.value)}
                                onKeyDown={e => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); submit(); } }}
                                placeholder="ጥያቄዎን ያስገቡ... / Gaaffii galchaa... / ሕቶ ኣእቱ..."
                                className="flex-1 bg-transparent border-none focus:outline-none resize-none text-sm text-[var(--text-primary)] placeholder:text-[var(--text-muted)] py-2 px-2 max-h-32 min-h-[40px]"
                                rows={1} />
                            <div className="flex items-center gap-1.5 pb-0.5">
                                {inputText.trim()
                                    ? <button type="submit" disabled={isProcessing}
                                        className="w-9 h-9 rounded-xl bg-gradient-to-br from-teal-500 to-emerald-500 flex items-center justify-center hover:scale-105 transition-transform disabled:opacity-50 shadow-md shadow-teal-500/30">
                                        <SendHorizontal className="w-4 h-4 text-white" />
                                    </button>
                                    : <MicButton isRecording={isRecording} startOp={startRec} stopOp={stopRec} />
                                }
                            </div>
                        </form>
                        <p className="text-center text-[10px] text-[var(--text-muted)] mt-2">
                            Grounded in Ethiopian MoH Clinical Guidelines · Emergency: 912
                        </p>
                    </div>
                </div>
            </div>
        </AppShell>
    );
}
