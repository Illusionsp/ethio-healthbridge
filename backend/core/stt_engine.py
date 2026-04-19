import os
import re
from google import genai
from dotenv import load_dotenv

load_dotenv()

_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
MODEL = "gemini-1.5-flash"


def clean_for_ai(text: str) -> str:
    """Standardizes Amharic characters for consistent database searching."""
    text = re.sub('[ሃኅኃሐሓኻ]', 'ሀ', text)
    text = re.sub('[ሠ]', 'ሰ', text)
    text = re.sub('[ዓኣዐ]', 'አ', text)
    text = re.sub('[ጸፀ]', 'ጸ', text)
    text = re.sub(r'[።፡፣፤፥፦፧፨፠]', ' ', text)
    return " ".join(text.split())


def transcribe_amharic(audio_path: str) -> str:
    """
    Transcribes audio in Amharic, Afaan Oromoo, or Tigrinya using Gemini.
    """
    if not os.path.exists(audio_path):
        print(f"Error: Audio file not found at {audio_path}")
        return "ይቅርታ፣ የድምፅ ፋይል አልተገኘም።"

    print("Sending audio to Gemini for transcription...")

    try:
        # Upload file using new SDK
        uploaded = _client.files.upload(file=audio_path)

        prompt = (
            "You are an expert linguist for Ethiopian languages. "
            "Listen to this audio and accurately transcribe exactly what is spoken. "
            "The speaker may be using Amharic, Afaan Oromoo, or Tigrinya. "
            "Return ONLY the transcribed text in the original language spoken, "
            "without any English words, translations, or introductory text. "
            "Medical terms like 'mitch', 'wugat', 'qurxummii', or 'hargansa' should be preserved as-is."
        )

        response = _client.models.generate_content(
            model=MODEL,
            contents=[prompt, uploaded]
        )

        # Clean up uploaded file
        _client.files.delete(name=uploaded.name)

        raw_text = response.text.strip() if response.text else ""
        print(f"Gemini Raw Output: '{raw_text}'")

        if not raw_text:
            return "ይቅርታ፣ ድምፅዎ አልተሰማም። እባክዎ በድጋሚ ይሞክሩ።"

        cleaned = clean_for_ai(raw_text)
        print(f"Cleaned Text for RAG: '{cleaned}'")
        return cleaned

    except Exception as e:
        print(f"Cloud Transcription Error: {e}")
        return "ይቅርታ፣ አሁን ላይ ድምፅዎን መስማት አልቻልኩም። እባክዎ ትንሽ ቆይተው ይሞክሩ።"
