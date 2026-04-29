from gtts import gTTS
import uuid
from pathlib import Path

AUDIO_DIR = Path("audio")
AUDIO_DIR.mkdir(exist_ok=True)

def synthesize_amharic(text: str) -> str:
    filename = f"{uuid.uuid4().hex}.mp3"
    filepath = AUDIO_DIR / filename

    tts = gTTS(text=text, lang="am")
    tts.save(str(filepath))

    return filename  # just the name, not full path