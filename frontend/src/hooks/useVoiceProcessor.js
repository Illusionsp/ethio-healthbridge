import { api } from "../lib/api";

export const useVoiceProcessor = () => {
    const processVoice = async (audioBlob, subCity = "Unknown") => {
        try {
            const formData = new FormData();
            formData.append("audio", audioBlob, "recording.mp3");
            formData.append("sub_city", subCity);
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
