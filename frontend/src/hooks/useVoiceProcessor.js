import { api } from "../lib/api";

export const useVoiceProcessor = () => {
    const processVoice = async (audioBlob) => {
        try {
            const formData = new FormData();
            formData.append("audio", audioBlob, "recording.mp3");
            const response = await api.post("/api/voice-chat", formData, {
                headers: {
                    "Content-Type": "multipart/form-data"
                }
            });
            return response.data;
        } catch (error) {
            console.error("Error processing voice:", error);
            throw error;
        }
    };

    return { processVoice };
}
