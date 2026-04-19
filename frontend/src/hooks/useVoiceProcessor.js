import { api } from "../lib/api";

export const useVoiceProcessor = () => {
    const processVoice = async (audioBlob, mode = "adult") => {
        const formData = new FormData();
        formData.append("audio", audioBlob, "recording.webm");
        formData.append("mode", mode);

        const response = await api.post("/api/voice-chat", formData, {
            headers: { "Content-Type": "multipart/form-data" }
        });
        return response.data;
    };

    return { processVoice };
};
