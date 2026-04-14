import os
from faster_whisper import WhisperModel

model = WhisperModel("base", device="cpu", compute_type="int8")

def transcribe_amharic(audio_path: str) -> str:
    if not os.path.exists(audio_path):
        return "Error: Audio file not found."

    print(f"👂 Transcribing audio: {audio_path}...")
    
    segments, info = model.transcribe(audio_path, language="am")
    full_text = "".join([segment.text for segment in segments])
    
    return full_text.strip()

if __name__ == "__main__":
    print(transcribe_amharic("backend/data/audio_outputs/test_input.wav"))