import os
import re
import uuid
from gtts import gTTS

# gTTS language codes for supported languages
# Tigrinya is not supported by gTTS, fall back to Amharic (same script)
LANG_CODES = {
    "Amharic": "am",
    "Tigrinya": "am",      # closest available
    "Afaan Oromoo": "om",  # Oromo is supported in newer gTTS
}

def _detect_lang_code(text: str) -> str:
    """Pick the best gTTS language code based on script/content."""
    # Afaan Oromoo uses Latin script with specific markers
    oromoo_markers = ["dhukkuba", "qufaa", "garaa", "hargansa", "qurxummii", "bilbilaa", "hatattama"]
    if any(m in text.lower() for m in oromoo_markers):
        return "om"
    return "am"  # Amharic / Tigrinya both use Ethiopic script


def generate_voice_response(text: str, filename: str = "") -> str:
    # Generate a unique filename if none provided, so responses never overwrite each other
    if not filename:
        filename = f"response_{uuid.uuid4().hex[:8]}.mp3"

    try:
        # Clean markdown symbols so TTS doesn't read them aloud
        clean_text = re.sub(r'[*#_\-]', '', text)
        clean_text = re.sub(r'\s+', ' ', clean_text).strip()
        clean_text = clean_text.replace(".", "።")

        lang_code = _detect_lang_code(clean_text)
        print(f"Generating voice [{lang_code}]: {clean_text[:40]}...")

        tts = gTTS(text=clean_text, lang=lang_code, slow=False)

        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        output_dir = os.path.join(base_dir, "data", "audio_outputs")
        os.makedirs(output_dir, exist_ok=True)
        file_path = os.path.join(output_dir, filename)

        tts.save(file_path)
        return file_path
    except Exception as e:
        print(f"TTS Error: {e}")
        return ""