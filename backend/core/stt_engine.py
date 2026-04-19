import os
import re
import google.generativeai as genai
from dotenv import load_dotenv

# Ensure environment variables are loaded
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def clean_for_ai(text: str) -> str:
    """Advanced Amharic character standardization for perfect database matching."""
    if not text:
        return ""
    # Group 1: The 'H' sounds
    text = re.sub('[ሃኅኃሐሓኻ]', 'ሀ', text)
    text = re.sub('[ሐሑሒሓሔሕሖ]', 'ሀ', text)
    # Group 2: Labialized/Complex sounds (Crucial for Amharic medical terms)
    text = re.sub('[ኈኊኋኌኍ]', 'ሁ', text) 
    # Group 3: S, A, and Ts sounds
    text = re.sub('[ሠ]', 'ሰ', text)
    text = re.sub('[ዓኣዐ]', 'አ', text)
    text = re.sub('[ጸፀ]', 'ጸ', text)
    # Group 4: Punctuation removal
    text = re.sub(r'[።፡፣፤፥፦፧፨፠?!.,]', ' ', text)
    return " ".join(text.split())

def transcribe_amharic(audio_path: str) -> str:
    if not os.path.exists(audio_path):
        print(f"❌ Error: Audio file not found at {audio_path}")
        return "ይቅርታ፣ የድምፅ ፋይል አልተገኘም።"

    print("☁️ Sending audio to Gemini Cloud for Super-Hearing Transcription...")
    
    try:
        audio_file = genai.upload_file(path=audio_path)
        
        # 1. Revert to your working 2.5 model
        model = genai.GenerativeModel('gemini-2.5-flash-lite')
        
        # 2. Keep the SUPER HEARING PROMPT
        prompt = (
            "You are an expert, high-fidelity Amharic Medical Scribe. "
            "Listen carefully to this audio. Even if there is background noise, focus strictly on the human speech. "
            "Transcribe EVERY SINGLE WORD exactly as spoken in Amharic script. "
            "Do not translate to English. Do not summarize. Do not fix grammar. "
            "Output ONLY the raw Amharic transcription."
        )
        
        # 3. Keep the ZERO TEMPERATURE (This prevents the hallucination/bad listening)
        response = model.generate_content(
            [prompt, audio_file],
            generation_config=genai.types.GenerationConfig(
                temperature=0.0,
                top_p=1,
                top_k=1
            )
        )
        genai.delete_file(audio_file.name)
        
        raw_text = response.text.strip()
        print(f"🗣️ Gemini Raw Output: '{raw_text}'")
        
        if not raw_text:
            print("⚠️ Gemini heard nothing.")
            return "ይቅርታ፣ ድምፅዎ አልተሰማም። እባክዎ በድጋሚ ይሞክሩ።"
            
        cleaned_text = clean_for_ai(raw_text)
        print(f"✨ Cleaned Text for RAG: '{cleaned_text}'")
        
        return cleaned_text
        
    except Exception as e:
        print(f"❌ Cloud Transcription Error: {e}")
        return "ይቅርታ፣ አሁን ላይ ድምፅዎን መስማት አልቻልኩም። እባክዎ ትንሽ ቆይተው ይሞክሩ።"

if __name__ == "__main__":
    print(transcribe_amharic("backend/data/audio_outputs/test_input.wav"))