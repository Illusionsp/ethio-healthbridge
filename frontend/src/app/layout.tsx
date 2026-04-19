import type { Metadata, Viewport } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({ subsets: ["latin"], variable: "--font-inter" });

export const metadata: Metadata = {
    title: "Ethio-HealthBridge",
    description: "Voice-first AI health assistant for Ethiopia — Amharic, Afaan Oromoo, Tigrinya",
    manifest: "/manifest.json",
    appleWebApp: { capable: true, statusBarStyle: "black-translucent", title: "HealthBridge" },
};

export const viewport: Viewport = {
    themeColor: "#020d18",
    width: "device-width",
    initialScale: 1,
    maximumScale: 1,
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
    return (
        <html lang="am" className={inter.variable}>
            <body>
                {children}
                <div id="modal-root" />
            </body>
        </html>
    );
}
