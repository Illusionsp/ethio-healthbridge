import os
import re
import google.generativeai as genai
from dotenv import load_dotenv

# Ensure environment variables are loaded
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def clean_for_ai(text: str) -> str:
    """Standardizes Amharic characters for consistent database searching."""
    text = re.sub('[ሃኅኃሐሓኻ]', 'ሀ', text)
    text = re.sub('[ሠ]', 'ሰ', text)
    text = re.sub('[ዓኣዐ]', 'አ', text)
    text = re.sub('[ጸፀ]', 'ጸ', text)
    text = re.sub(r'[።፡፣፤፥፦፧፨፠]', ' ', text)
    return " ".join(text.split())

def transcribe_amharic(audio_path: str) -> str:
    if not os.path.exists(audio_path):
        print(f"❌ Error: Audio file not found at {audio_path}")
        # 1. NEW: Speak to the user if the mic failed
        return "ይቅርታ፣ የድምፅ ፋይል አልተገኘም።" # "Sorry, the audio file was not found."

    print("☁️ Sending audio to Gemini Cloud for Amharic Transcription...")
    
    try:
        # 1. Upload the audio file to Google's temporary memory
        audio_file = genai.upload_file(path=audio_path)
        
        # 2. Initialize the Multimodal AI
        model = genai.GenerativeModel('gemini-2.5-flash-lite')
        
        # 3. Strict Prompting to prevent it from translating or adding conversational text
        prompt = (
            "You are an expert Amharic linguist. Listen to this audio and accurately "
            "transcribe exactly what is spoken in Amharic. "
            "Return ONLY the Amharic text, without any English words, translations, or introductory text."
        )
        
        # 4. Process the audio and text together
        response = model.generate_content([prompt, audio_file])
        
        # 5. Clean up the file from Google's servers to save your quota space
        genai.delete_file(audio_file.name)
        
        raw_text = response.text.strip()
        print(f"🗣️ Gemini Raw Output: '{raw_text}'")
        
        # Safety check if the audio was silent
        if not raw_text:
            print("⚠️ Gemini heard nothing.")
            # 2. NEW: Speak to the user if the audio was completely silent
            return "ይቅርታ፣ ድምፅዎ አልተሰማም። እባክዎ በድጋሚ ይሞክሩ።" # "Sorry, your voice was not heard. Please try again."
            
        cleaned_text = clean_for_ai(raw_text)
        print(f"✨ Cleaned Text for RAG: '{cleaned_text}'")
        
        return cleaned_text
        
    except Exception as e:
        print(f"❌ Cloud Transcription Error: {e}")
        # 3. NEW: Speak to the user if the cloud API fails (e.g., quota limit)
        return "ይቅርታ፣ አሁን ላይ ድምፅዎን መስማት አልቻልኩም። እባክዎ ትንሽ ቆይተው ይሞክሩ።" # "Sorry, I couldn't hear your voice right now. Please try a bit later."

if __name__ == "__main__":
    # Test the cloud engine
    print(transcribe_amharic("backend/data/audio_outputs/test_input.wav"))