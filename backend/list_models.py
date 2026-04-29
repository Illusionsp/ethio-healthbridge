from dotenv import load_dotenv
import os
from google import genai

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

print("Your available Gemini models:")
for model in client.models.list():
    print(f"- {model.name} ({model.display_name})")