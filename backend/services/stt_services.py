# app/services/stt_service_elevenlabs.py

from io import BytesIO
import requests

ELEVENLABS_API_KEY = "sk_795537afc8899e509a2aca0b1f72db3838fdd03526c2e6c3"  # your key

STT_URL = "https://api.elevenlabs.io/v1/speech-to-text"  # [web:97]
MODEL_ID = "scribe_v2"
LANGUAGE_CODE = "am"

# Each keyword must be short (< 50 chars)
KEYWORDS = [
    "ራስ ምታት",        # headache
    "ልብ ህመም",        # chest pain
    "ደም ግፊት",        # blood pressure
    "ሳል",              # cough
    "ሙቀት",            # fever
    "አስም",          # asthma
    "መድሀኒት",         # medicine
    "ህፃን",            # child
    "እርግዝና",        # pregnancy
    "ድንገተኛ ሕመም",   # emergency illness
    "ምች",            # shortness of breath
    "ዉጋት",           # weakness
    "ጤና መመሪያ",      # health guideline
    "EPHCG",
]

def transcribe_amharic(audio_bytes: bytes) -> dict:
    files = {
        "file": ("audio.wav", BytesIO(audio_bytes), "audio/wav"),
    }

    # From the error, ElevenLabs expects a 'keywords' parameter
    # with a list/array of short keyword strings. [web:97][web:96]
    data = {
        "model_id": MODEL_ID,
        "language_code": LANGUAGE_CODE,
        "diarize": "false",
        "tag_audio_events": "false",
    }

    # Attach keywords as separate entries
    # Depending on the exact API, this may be either:
    #   keywords=word1&keywords=word2&...
    # or a JSON array in a JSON body.
    # The simplest form-data way:
    for kw in KEYWORDS:
        data.setdefault("keywords", [])
        data["keywords"].append(kw)

    headers = {
        "xi-api-key": ELEVENLABS_API_KEY,
    }

    resp = requests.post(STT_URL, headers=headers, files=files, data=data, timeout=60)

    if resp.status_code != 200:
        raise RuntimeError(f"ElevenLabs STT failed: {resp.status_code} - {resp.text}")

    result = resp.json()
    text = result.get("text", "").strip()

    return {
        "text": text,
        "language": "am",
        "raw": result,
    }