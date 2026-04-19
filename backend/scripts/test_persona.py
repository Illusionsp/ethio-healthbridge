import sys
import os
import asyncio

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), ".."))

from core.rag_engine import query_medical_guidelines

async def test_chat_persona():
    print("Testing Chat Persona...")
    sample_text = "ራስ ምታት አለኝ። ምን ላድርግ?" # I have a headache. What should I do?
    
    user_id = "test_user_persona"
    result = query_medical_guidelines(sample_text, user_id)
    
    print("\n--- AI Response ---")
    print(result.get("response_text", "No response"))
    
    response_text = result.get("response_text", "")
    if "ፈጣሪ ምህረቱን ያምጣልዎ" in response_text:
        print("\n✅ Signature found.")
    else:
        print("\n❌ Signature NOT found.")
        
    if "ዶክተር" in response_text or "Doctor" in response_text:
        print("✅ Doctor persona detected.")

if __name__ == "__main__":
    asyncio.run(test_chat_persona())
