import os
import re
import asyncio
import uuid
from gtts import gTTS
import edge_tts

# We use the premium Neural female voice for Amharic
PRIMARY_VOICE = "am-ET-MekdesNeural"

def _clean_amharic_text(text: str) -> str:
    """Cleans markdown, weird spaces, and fixes punctuation for smooth Amharic TTS."""
    # Removes asterisks (*), hashtags (#), dashes (-), and underscores (_)
    clean_text = re.sub(r'[*#_\-]', '', text)
    
    # Replaces multiple newlines or spaces with a single space
    clean_text = re.sub(r'\s+', ' ', clean_text).strip()
    
    # Replaces English periods with Amharic 'Arat Neteb' (።)
    clean_text = clean_text.replace(".", "።")
    
    return clean_text

async def _generate_edge_tts(text: str, output_path: str):
    """Hidden async function to handle the Microsoft Edge connection."""
    communicate = edge_tts.Communicate(text, PRIMARY_VOICE)
    await communicate.save(output_path)

# 1. CHANGED: Added 'async' here
async def generate_voice_response(text: str, filename: str = None) -> str:
    """Generates clean Amharic audio with a graceful fallback to gTTS."""
    try:
        # 1. APPLY YOUR CLEANING LOGIC
        clean_text = _clean_amharic_text(text)
        print(f"🗣️ Generating Smooth Voice: {clean_text[:30]}...")
        
        # 2. YOUR DYNAMIC PATH LOGIC
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        output_dir = os.path.join(base_dir, "data", "audio_outputs")
        os.makedirs(output_dir, exist_ok=True)
        
        # 3. CONCURRENCY SAFETY
        if not filename:
            filename = f"response_{uuid.uuid4().hex[:8]}.mp3"
            
        file_path = os.path.join(output_dir, filename)
        
        # 4. THE PRIMARY ENGINE (Microsoft edge-tts)
        try:
            # 2. CHANGED: We use 'await' instead of 'asyncio.run'
            await _generate_edge_tts(clean_text, file_path)
            print("✅ TTS Success: Generated high-quality neural audio (Mekdes).")
            return file_path
            
        # 5. THE GRACEFUL FALLBACK (Google gTTS)
        except Exception as e:
            print(f"⚠️ edge-tts failed ({e}). Triggering gTTS fallback...")
            
            tts = gTTS(text=clean_text, lang='am', slow=False)
            tts.save(file_path)
            print("✅ TTS Success: Generated audio using gTTS fallback.")
            return file_path

    except Exception as critical_error:
        print(f"❌ Critical TTS Failure: {critical_error}")
        return ""

    except Exception as critical_error:
        print(f"❌ Critical TTS Failure: {critical_error}")
        return ""

if __name__ == "__main__":
    # Test with a messy string to prove cleaning and fallback logic works
    test_text = "*ጤና ይስጥልኝ*፣ - ዛሬ እንዴት ልረዳዎ እችላለሁ?"
    result = generate_voice_response(test_text)
    
    if result:
        print(f"🎉 Awesome! Audio perfectly saved to: {result}")