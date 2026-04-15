import os
from google.cloud import texttospeech

def generate_voice_response(text: str, filename: str = "ai_response.mp3") -> str:
    client = texttospeech.TextToSpeechClient()
    synthesis_input = texttospeech.SynthesisInput(text=text)

    voice = texttospeech.VoiceSelectionParams(
        language_code="am-ET",
        name="am-ET-Wavenet-A",
        ssml_gender=texttospeech.SsmlVoiceGender.FEMALE
    )

    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3,
        speaking_rate=0.90,
        pitch=0.0
    )

    try:
        print(f"🗣️ Gemini TTS is synthesizing: {text[:30]}...")
        response = client.synthesize_speech(
            input=synthesis_input, voice=voice, audio_config=audio_config
        )

        output_dir = "backend/data/audio_outputs"
        os.makedirs(output_dir, exist_ok=True)
        file_path = os.path.join(output_dir, filename)

        with open(file_path, "wb") as out:
            out.write(response.audio_content)
            
        return file_path
    except Exception as e:
        print(f"Gemini TTS Error: {e}")
        return ""

if __name__ == "__main__":
    test_text = "ጤና ይስጥልኝ፣ ዛሬ እንዴት ልረዳዎ እችላለሁ?"
    generate_voice_response(test_text)