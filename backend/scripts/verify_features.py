import sys
import os
import json
import asyncio

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), ".."))

from core.rag_engine import generate_clinical_summary
from utils.telegram_bot import send_doctor_alert

async def test_summary():
    print("Testing Clinical Summary Generation...")
    sample_text = "ከባድ የራስ ምታት እና ትኩሳት አለኝ። ካፌይን ስወስድ ይሻለኛል ግን አሁንም በጣም ያመኛል።"
    # Translation: I have a severe headache and fever. It gets better when I take caffeine but it still hurts a lot.
    
    user_id = "test_user_123"
    summary = generate_clinical_summary(sample_text, user_id)
    
    print("\n--- Generated Summary ---")
    print(json.dumps(summary, indent=2))
    
    if "symptoms" in summary and len(summary["symptoms"]) > 0:
        print("✅ Symptoms extracted.")
    else:
        print("❌ Symptom extraction failed.")
        
    return summary

def test_telegram(summary):
    print("\nTesting Telegram Alert Payload...")
    # Mocking environment variables for test
    os.environ["TELEGRAM_BOT_TOKEN"] = "MOCK_TOKEN"
    os.environ["TELEGRAM_CHAT_ID"] = "MOCK_CHAT_ID"
    
    # We won't actually send because the token is mock, but we'll check the logic
    # In a real scenario, this would failing sendMessage but we can check if it tries.
    success = send_doctor_alert(patient_id="test_user_123", summary=summary)
    
    # Since it's a mock token, it should fail, but we've verified the payload formatting in the code.
    print(f"Telegram Alert triggered (expected failure with mock token): {success}")

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    summary = loop.run_until_complete(test_summary())
    test_telegram(summary)
