import axios from "axios";

// In production, set NEXT_PUBLIC_API_URL to your Railway/Render backend URL
// In development, falls back to localhost:8000
const BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export const api = axios.create({
    baseURL: BASE_URL,
    headers: {
        "Content-Type": "application/json"
    }
});
