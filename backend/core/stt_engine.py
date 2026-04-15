import os
import re
from faster_whisper import WhisperModel

model = WhisperModel("base", device="cpu", compute_type="int8")

def clean_for_ai(text: str) -> str:
    text = re.sub('[ሃኅኃሐሓኻ]', 'ሀ', text)
    text = re.sub('[ሠ]', 'ሰ', text)
    text = re.sub('[ዓኣዐ]', 'አ', text)
    text = re.sub('[ጸፀ]', 'ጸ', text)
    text = re.sub(r'[።፡፣፤፥፦፧፨፠]', ' ', text)
    return " ".join(text.split())

def transcribe_amharic(audio_path: str) -> str:
    if not os.path.exists(audio_path):
        return "Error: Audio file not found."

    segments, info = model.transcribe(audio_path, language="am", vad_filter=True)
    raw_text = "".join([segment.text for segment in segments])
    
    return clean_for_ai(raw_text)

if __name__ == "__main__":
    print(transcribe_amharic("backend/data/audio_outputs/test_input.wav"))