import os
from gtts import gTTS

def generate_voice_response(text: str, filename: str = "ai_response.mp3") -> str:
    try:
        print(f"🗣️ Generating Voice: {text[:30]}...")
        tts = gTTS(text=text, lang='am', slow=False)
        
        # FIXED: Removed the nested 'backend/' path so it saves correctly
        output_dir = "data/audio_outputs"
        os.makedirs(output_dir, exist_ok=True)
        file_path = os.path.join(output_dir, filename)
        
        tts.save(file_path)
        return file_path
    except Exception as e:
        print(f"TTS Error: {e}")
        return ""

if __name__ == "__main__":
    test_text = "ጤና ይስጥልኝ፣ ዛሬ እንዴት ልረዳዎ እችላለሁ?"
    print("Testing Amharic TTS...")
    result = generate_voice_response(test_text)
    if result:
        print(f"Success! Audio saved to: {result}")