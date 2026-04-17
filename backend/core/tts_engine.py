import os
import re
from gtts import gTTS

def generate_voice_response(text: str, filename: str = "ai_response.mp3") -> str:
    try:
        # 1. CLEANING LOGIC (The "Smooth" Fix)
        # This removes asterisks (*), hashtags (#), dashes (-), and underscores (_)
        # so the AI doesn't say "asterisk" out loud.
        clean_text = re.sub(r'[*#_\-]', '', text)
        
        # 2. SPACE LOGIC
        # Replaces multiple newlines or spaces with a single space to avoid "glitchy" pauses
        clean_text = re.sub(r'\s+', ' ', clean_text).strip()
        
        # 3. AMHARIC PAUSE FIX
        # Replacing English periods with Amharic 'Arat Neteb' (።) helps the engine breathe correctly
        clean_text = clean_text.replace(".", "።")

        print(f"🗣️ Generating Smooth Voice: {clean_text[:30]}...")
        
        # Use the CLEANED text for TTS
        tts = gTTS(text=clean_text, lang='am', slow=False)
        
        # PATH LOGIC (Based on your tree structure)
        # We ensure we are in the backend/data/audio_outputs directory
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        output_dir = os.path.join(base_dir, "data", "audio_outputs")
        os.makedirs(output_dir, exist_ok=True)
        file_path = os.path.join(output_dir, filename)
        
        tts.save(file_path)
        return file_path
    except Exception as e:
        print(f"TTS Error: {e}")
        return ""

if __name__ == "__main__":
    # Test with a messy string to prove it works
    test_text = "*ጤና ይስጥልኝ*፣ - ዛሬ እንዴት ልረዳዎ እችላለሁ?"
    result = generate_voice_response(test_text)
    if result:
        print(f"Success! Audio saved to: {result}")