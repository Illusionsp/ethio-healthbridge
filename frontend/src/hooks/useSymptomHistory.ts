import { useState, useEffect } from "react";

export type SymptomEntry = {
    id: string;
    timestamp: number; // Unix ms
    symptoms: string;  // raw user text
    response: string;  // AI response
    language: string;
};

const STORAGE_KEY = "ethio-symptom-history";
const MAX_ENTRIES = 20;

export function useSymptomHistory() {
    const [history, setHistory] = useState<SymptomEntry[]>([]);

    useEffect(() => {
        try {
            const raw = localStorage.getItem(STORAGE_KEY);
            if (raw) setHistory(JSON.parse(raw));
        } catch {
            setHistory([]);
        }
    }, []);

    const addEntry = (symptoms: string, response: string, language = "Amharic") => {
        const entry: SymptomEntry = {
            id: Date.now().toString(),
            timestamp: Date.now(),
            symptoms,
            response,
            language,
        };
        setHistory(prev => {
            const updated = [entry, ...prev].slice(0, MAX_ENTRIES);
            localStorage.setItem(STORAGE_KEY, JSON.stringify(updated));
            return updated;
        });
    };

    const clearHistory = () => {
        localStorage.removeItem(STORAGE_KEY);
        setHistory([]);
    };

    // Returns the most recent entry if it was within the last 48 hours
    const getRecentEntry = (): SymptomEntry | null => {
        if (history.length === 0) return null;
        const latest = history[0];
        const hoursSince = (Date.now() - latest.timestamp) / (1000 * 60 * 60);
        return hoursSince <= 48 ? latest : null;
    };

    return { history, addEntry, clearHistory, getRecentEntry };
}
