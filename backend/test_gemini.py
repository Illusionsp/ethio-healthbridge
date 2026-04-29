from dotenv import load_dotenv
import os
from google import genai

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

model = client.models.generate_content(
    model="gemini-2.5-flash",  # Updated model name
    contents="Test Amharic: ሰላም ልዩ?"
)
print("✅ Gemini OK:", model.text)