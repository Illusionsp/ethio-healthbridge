"use client";
import AppShell from "../../components/AppShell";
import { Info, Mic, Brain, Eye, MapPin, Baby, History, Wifi, Shield, Heart, ExternalLink } from "lucide-react";

const FEATURES = [
    { icon: Mic, title: "Voice-First STT", desc: "Speak in Amharic, Afaan Oromoo, or Tigrinya. Gemini transcribes your voice with medical term awareness.", color: "teal" },
    { icon: Brain, title: "Medical RAG", desc: "Answers grounded strictly in Ethiopian Ministry of Health Clinical Guidelines via ChromaDB vector search.", color: "emerald" },
    { icon: Eye, title: "Medicine Scanner", desc: "Upload a medicine label photo. Gemini Vision extracts name, dosage, expiry date, and warnings in Amharic.", color: "blue" },
    { icon: MapPin, title: "Facility Finder", desc: "Finds nearest hospitals, clinics, health posts, and pharmacies using OpenStreetMap — no API key needed.", color: "cyan" },
    { icon: Baby, title: "Child Health Mode", desc: "Pediatric-adjusted responses. Asks for age and weight, adjusts dosage guidance for children.", color: "amber" },
    { icon: History, title: "Symptom History", desc: "Tracks your consultations locally. Follow-up prompts remind you to check in after 48 hours.", color: "purple" },
    { icon: Wifi, title: "Offline / PWA", desc: "Installable as a mobile app. Works offline with cached responses and graceful Amharic fallback messages.", color: "indigo" },
    { icon: Shield, title: "Emergency Detection", desc: "Real-time red-flag symptom detection in all 3 languages. Instantly shows 912 call button.", color: "red" },
];

const STACK = [
    { layer: "Voice (STT)", tech: "Gemini 2.0 Flash", note: "Amharic / Oromoo / Tigrinya" },
    { layer: "Speech (TTS)", tech: "gTTS", note: "Amharic & Oromo voice" },
    { layer: "AI Brain", tech: "Gemini 2.0 Flash", note: "RAG + Vision" },
    { layer: "Embeddings", tech: "text-embedding-004", note: "Google GenAI" },
    { layer: "Vector DB", tech: "ChromaDB", note: "204 MoH chunks" },
    { layer: "Backend", tech: "FastAPI", note: "Python 3.13" },
    { layer: "Frontend", tech: "Next.js 14", note: "React 18 + Tailwind" },
    { layer: "Knowledge", tech: "EPHCG 2017", note: "158 pages ingested" },
];

export default function AboutPage() {
    return (
        <AppShell>
            <div className="flex flex-col h-full overflow-hidden">
                <div className="flex-none px-6 py-4 glass-bright border-b border-[var(--border)]">
                    <div className="flex items-center gap-2">
                        <Info className="w-5 h-5 text-[var(--accent-teal)]" />
                        <h1 className="text-base font-bold text-[var(--text-primary)]">About</h1>
                        <span className="text-xs text-[var(--text-muted)]">ስለ እኛ</span>
                    </div>
                </div>

                <div className="flex-1 overflow-y-auto px-6 py-5 space-y-6">
                    {/* Hero */}
                    <div className="glass rounded-2xl p-6 border border-[var(--border)] text-center relative overflow-hidden">
                        <div className="absolute inset-0 bg-gradient-to-br from-teal-500/5 to-emerald-500/5" />
                        <div className="relative">
                            <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-teal-400 to-emerald-500 flex items-center justify-center mx-auto mb-3 shadow-lg shadow-teal-500/30">
                                <Heart className="w-7 h-7 text-white" />
                            </div>
                            <h2 className="text-xl font-bold text-[var(--text-primary)] mb-1">Ethio-HealthBridge</h2>
                            <p className="text-sm text-[var(--text-secondary)] max-w-md mx-auto leading-relaxed">
                                A voice-first AI health assistant designed to bridge the gap between Ethiopian communities and medical guidance — in their own languages.
                            </p>
                            <div className="flex items-center justify-center gap-3 mt-4">
                                {["🇪🇹 Ethiopia", "🗣️ 3 Languages", "🏥 MoH Grounded"].map(t => (
                                    <span key={t} className="text-xs px-2.5 py-1 rounded-full bg-teal-500/10 border border-teal-500/20 text-teal-300">{t}</span>
                                ))}
                            </div>
                        </div>
                    </div>

                    {/* Problem */}
                    <div className="glass rounded-2xl p-5 border border-[var(--border)]">
                        <p className="text-xs font-semibold text-[var(--text-secondary)] uppercase tracking-wider mb-2">Problem Statement</p>
                        <p className="text-sm text-[var(--text-secondary)] leading-relaxed">
                            In Ethiopia, many people face delays in getting medical guidance because doctors are far away, language barriers exist, and health information is not always accessible. People often describe symptoms using local expressions like <span className="text-teal-300 font-medium">"mitch"</span> or <span className="text-teal-300 font-medium">"wugat"</span> which generic AI systems don't understand.
                        </p>
                    </div>

                    {/* Features grid */}
                    <div>
                        <p className="text-xs font-semibold text-[var(--text-secondary)] uppercase tracking-wider mb-3">Features</p>
                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                            {FEATURES.map(({ icon: Icon, title, desc, color }) => (
                                <div key={title} className="glass rounded-2xl p-4 border border-[var(--border)] hover:border-teal-500/20 transition-all">
                                    <div className={`w-8 h-8 rounded-xl bg-${color}-500/10 border border-${color}-500/20 flex items-center justify-center mb-2`}>
                                        <Icon className={`w-4 h-4 text-${color}-400`} />
                                    </div>
                                    <p className="text-sm font-semibold text-[var(--text-primary)] mb-1">{title}</p>
                                    <p className="text-xs text-[var(--text-secondary)] leading-relaxed">{desc}</p>
                                </div>
                            ))}
                        </div>
                    </div>

                    {/* Tech stack */}
                    <div className="glass rounded-2xl border border-[var(--border)] overflow-hidden">
                        <div className="px-4 py-3 border-b border-[var(--border)]">
                            <p className="text-xs font-semibold text-[var(--text-secondary)] uppercase tracking-wider">Tech Stack</p>
                        </div>
                        <div className="divide-y divide-[var(--border)]">
                            {STACK.map(({ layer, tech, note }) => (
                                <div key={layer} className="flex items-center justify-between px-4 py-2.5">
                                    <span className="text-xs text-[var(--text-muted)] w-28">{layer}</span>
                                    <span className="text-sm font-medium text-[var(--accent-teal)]">{tech}</span>
                                    <span className="text-xs text-[var(--text-muted)] text-right">{note}</span>
                                </div>
                            ))}
                        </div>
                    </div>

                    {/* Disclaimer */}
                    <div className="glass rounded-2xl p-4 border border-amber-500/20 bg-amber-500/5">
                        <p className="text-xs text-amber-300 font-semibold mb-1">⚠️ Disclaimer</p>
                        <p className="text-xs text-[var(--text-secondary)] leading-relaxed">
                            This is a prototype built for demonstration purposes. For real medical emergencies, always call <span className="text-red-400 font-bold">912</span> or visit your nearest health facility. Do not rely solely on AI for medical decisions.
                        </p>
                    </div>

                    <div className="h-4" />
                </div>
            </div>
        </AppShell>
    );
}
