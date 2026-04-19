import os
import chromadb
from llama_index.core import VectorStoreIndex, StorageContext, Settings
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.llms.gemini import Gemini
from utils.text_utils import clean_latin_script
from llama_index.embeddings.gemini import GeminiEmbedding
from llama_index.core.memory import ChatMemoryBuffer
from llama_index.core.storage.chat_store import SimpleChatStore
from dotenv import load_dotenv

# Ensure the .env is loaded so the API key is visible to LlamaIndex
load_dotenv()

try:
    # 1. SWITCHED TO FLASH-LITE for higher daily quota (1,000 RPD)
    Settings.llm = Gemini(model_name="models/gemini-2.5-flash-lite")
    
    # Matching the embedding model used during ingestion
    Settings.embed_model = GeminiEmbedding(model_name="models/gemini-embedding-001")
except Exception as e:
    print(f"Warning: Could not initialize Gemini or Embedding Model. {e}")

# 2. FILE PATHS
DB_PATH = "data/vector_db"
STORAGE_DIR = "data/storage"
CHAT_STORE_FILE = os.path.join(STORAGE_DIR, "chat_store.json")

# 3. INITIALIZE PERSISTENT STORAGE
os.makedirs(STORAGE_DIR, exist_ok=True)
if os.path.exists(CHAT_STORE_FILE):
    chat_store = SimpleChatStore.from_persist_path(CHAT_STORE_FILE)
else:
    chat_store = SimpleChatStore()

def get_db_collection():
    os.makedirs(DB_PATH, exist_ok=True)
    db = chromadb.PersistentClient(path=DB_PATH)
    return db.get_or_create_collection("moh_guidelines")

# 4. UPDATED SIGNATURE: Now accepts user_id
def query_medical_guidelines(query_text: str, user_id: str = "guest_user") -> dict:
    print(f"🔍 የፍለጋ ጥያቄ፡ '{query_text}' ለታካሚ መለያ፡ '{user_id}'")
    
    # --- 🛡️ SAFETY CHECK: BLANK AUDIO ---
    if not query_text or query_text.strip() == "":
        return {"response_text": "እባክዎ ጥያቄዎን በድጋሚ ይናገሩ። ድምፅዎ አልተሰማም።", "citations": []}
    
    # --- 👋 GREETINGS CHECK ---
    user_input = query_text.lower().strip()
    greetings = ["hi", "hello", "hey", "ሰላም", "ጤና ይስጥልኝ"]
    
    if user_input in greetings:
        return {"response_text": "ጤና ይስጥልኝ! እኔ ጤናለአዳም ነኝ። በኢትዮጵያ ጤና ሚኒስቴር መመሪያዎች ላይ ተመስርቼ ስለ ጤናዎ መረጃ በመስጠት ልረዳዎ እችላለሁ። እንዴት ልርዳዎ?", "citations": []}
    # ---------------------------

    try:
        collection = get_db_collection()
        
        # Fallback if DB is empty
        if collection.count() == 0:
            return _basic_llm_response(query_text)
            
        vector_store = ChromaVectorStore(chroma_collection=collection)
        storage_context = StorageContext.from_defaults(vector_store=vector_store)
        index = VectorStoreIndex.from_vector_store(vector_store, storage_context=storage_context)
        
        # 5. INITIALIZE MEMORY FOR THIS SPECIFIC USER
        memory = ChatMemoryBuffer.from_defaults(
            token_limit=3000, 
            chat_store=chat_store, 
            chat_store_key=user_id
        )

        # 6. SYSTEM PROMPT (Doctor Persona + Amharic Only + Smooth TTS)
        custom_system_prompt = (
            "You are 'Dr. Tena LeAdam' (ዶክተር ጤናለአዳም), a highly compassionate and professional medical doctor. "
            "Your tone is warm, reassuring, and culturally respectful.\n\n"
            "STRICT RULES:\n"
            "CRITICAL RULE: USE AMHARIC SCRIPT ONLY. ABSOLUTELY NO LATIN CHARACTERS (A-Z) ARE ALLOWED IN ANY PART OF YOUR RESPONSE.\n\n"
            "STRICT RULES:\n"
            "1. ZERO TOLERANCE FOR ENGLISH: Do not write 'Malaria', '(Malaria)', 'MoH', or any other Latin-script words. Even if you are writing a scientific name, it MUST be transliterated into Amharic script (e.g., ፕላዝሞዲየም). Any response containing a single Latin character is a failure.\n"
            "2. MEDICAL TERMS: Do not put English medical terms in parentheses. If you use a medical term, write it only in Amharic script. Example: 'ክሎሮኩዊን' (CORRECT) vs 'ክሎሮኩዊን (chloroquine)' (FORBIDDEN).\n"
            "3. TRANSLATE/TRANSLITERATE EVERYTHING: If a term exists in Amharic, use it. If not, transliterate the sound into Amharic characters. NEVER use English characters.\n"
            "4. AMHARIC ONLY: Your 'chat_response' MUST be 100% Amharic script.\n"
            "5. DOCTOR PERSONA: Maintain your professional 'Dr. Tena LeAdam' (ጤናለአዳም) tone.\n"
            "6. SMOOTH TTS FLOW: Use Amharic punctuation (፣ and ።) for pauses.\n"
            "7. SIGNATURE: End every response with 'ፈጣሪ ምህረቱን ያምጣልዎ።'\n"
            "8. EXPLICIT REFERENCING: State 'በኢትዮጵያ ጤና ሚኒስቴር መመሪያ መሰረት'.\n\n"
            "NEGATIVE EXAMPLES (NEVER DO THIS):\n"
            "- ማላሪያ (Malaria) -> WRONG (Contains English)\n"
            "- Plasmodium -> WRONG (Latin script)\n"
            "- MoH መመሪያ -> WRONG (Contains Latin script)\n\n"
            "POSITIVE EXAMPLES (ALWAYS DO THIS):\n"
            "- ማላሪያ -> CORRECT\n"
            "- ፕላዝሞዲየም -> CORRECT\n"
            "- በጤና ሚኒስቴር መመሪያ -> CORRECT\n\n"
            "Context information is below.\n--------------------\n{context_str}\n--------------------"
        )

        # 7. UNIFIED OUTPUT INSTRUCTIONS (JSON Schema)
        json_instruction = (
            "\n\nYou MUST return your response as a JSON object with the following structure:\n"
            "{\n"
            "  \"chat_response\": \"<Your 100% AMHARIC SCRIPT response here>\",\n"
            "  \"triage_summary\": {\n"
            "    \"symptoms\": [\"<Symptoms in English for doctors>\"],\n"
            "    \"urgency\": \"High/Medium/Low\",\n"
            "    \"ai_analysis\": \"<Assessment in English for doctors>\",\n"
            "    \"recommended_action\": \"<Action in English for doctors>\"\n"
            "  }\n"
            "}\n"
            "NOTE: The 'triage_summary' fields are for medical staff and MUST be in English. "
            "HOWEVER, the 'chat_response' MUST be 100% Amharic script with ZERO English characters."
        )

        chat_engine = index.as_chat_engine(
            chat_mode="context",
            memory=memory,
            system_prompt=custom_system_prompt + json_instruction,
            similarity_top_k=3
        )
        
        response = chat_engine.chat(query_text)
        raw_response = str(response)
        
        # 8. PARSE UNIFIED RESPONSE & STRIP LATIN PARENTHETICALS
        import json
        import re

        try:
            # Find JSON block
            json_match = re.search(r'\{.*\}', raw_response, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
                response_text = data.get("chat_response", raw_response)
                patient_summary = data.get("triage_summary", {})
                
                # Hard-clean the chat response with centralized logic
                response_text = clean_latin_script(response_text)
            else:
                response_text = clean_latin_script(raw_response)
                patient_summary = None
        except Exception:
            response_text = clean_latin_script(raw_response)
            patient_summary = None

        # 9. EXTRACT METADATA CITATIONS SAFELY
        citations_data = []
        if response.source_nodes:
            for node in response.source_nodes:
                fname = node.metadata.get('file_name', 'MoH Document')
                page = node.metadata.get('page_label', 'N/A')
                citations_data.append({"file_name": fname, "page_label": str(page)})

        # Remove duplicate citations
        unique_citations = []
        seen = set()
        for c in citations_data:
            key = (c["file_name"], c["page_label"])
            if key not in seen:
                seen.add(key)
                unique_citations.append(c)

        return {
            "response_text": response_text,
            "citations": unique_citations,
            "patient_summary": patient_summary
        }
        
    except Exception as e:
        print(f"የሲስተም ስህተት፡ {e}")
        error_msg = "ይቅርታ፣ አሁን ላይ መረጃ ማግኘት አልቻልኩም። እባክዎ ወደ ጤና ተቋም ይሂዱ። ፈጣሪ ምህረቱን ያምጣልዎ።"
        if "429" in str(e) or "Resource exhausted" in str(e):
            error_msg = "ይቅርታ፣ አገልግሎቱ በአሁኑ ጊዜ ተጨናንቋል። እባክዎ ከትንሽ ጊዜ በኋላ ይሞክሩ። ፈጣሪ ምህረቱን ያምጣልዎ።"
            
        return {
            "response_text": error_msg,
            "citations": [],
            "patient_summary": None
        }

def _basic_llm_response(query_text: str) -> dict:
    return {
        "response_text": (
            "ጤና ይስጥልኝ፣ እኔ ጤናለአዳም ነኝ። "
            "የሕክምና መመሪያ ማከማቻው በአሁኑ ጊዜ ባዶ ስለሆነ ዝርዝር መረጃ ማግኘት አልቻልኩም። "
            "ነገር ግን፣ አፋጣኝ ሕክምና የሚያስፈልግዎ ከሆነ ወደ ጥቁር አንበሳ ሆስፒታል ወይም በአቅራቢያዎ ወደሚገኝ ጤና ጣቢያ እንዲሄዱ እመክራለሁ። "
            "ለድንገተኛ አደጋ ዘጠኝ አንድ ሁለት (912) ላይ ይደውሉ። "
            "ፈጣሪ ምህረቱን ያምጣልዎ።"
        ),
        "citations": []
    }
def generate_clinical_summary(query_text: str, user_id: str) -> dict:
    """
    Generates a structured clinical summary for doctors.
    """
    print(f"🏥 Generating clinical summary for: {user_id}")
    
    prompt = (
        "You are a medical triage assistant. Analyze the following patient query (in Amharic) "
        "and provide a structured clinical summary in English for a doctor.\n\n"
        f"Patient Query: {query_text}\n\n"
        "Return a JSON object with the following fields:\n"
        "- symptoms: A list of extracted symptoms (in English).\n"
        "- raw_amharic: The original Amharic symptoms extracted.\n"
        "- urgency: 'High', 'Medium', or 'Low'.\n"
        "- ai_analysis: A brief medical assessment/possible mapping to MoH protocols.\n"
        "- recommended_action: Immediate next step for the triage team.\n"
    )
    
    try:
        from llama_index.core import Settings
        # Using the direct model call for structured output
        llm = Settings.llm
        if not llm:
            return {"error": "LLM not initialized"}
            
        response = llm.complete(prompt)
        
        # Simple parsing if it's not strictly JSON
        import json
        import re
        
        # Try to find JSON in the response
        match = re.search(r"\{.*\}", str(response), re.DOTALL)
        if match:
            # Basic cleanup of markdown code blocks if present
            cleaned_json = match.group().strip()
            summary_data = json.loads(cleaned_json)
        else:
            # Fallback if parsing fails
            summary_data = {
                "symptoms": ["Analysis failed to extract JSON"],
                "raw_amharic": query_text,
                "urgency": "Medium",
                "ai_analysis": str(response),
                "recommended_action": "Evaluate patient manually."
            }
        
        summary_data["patient_id"] = user_id
        return summary_data
    except Exception as e:
        print(f"Summary Generation Error: {e}")
        return {
            "symptoms": [],
            "raw_amharic": query_text,
            "urgency": "Error",
            "ai_analysis": f"Critical error in summary generation: {str(e)}",
            "recommended_action": "Check system logs and evaluate patient manually.",
            "patient_id": user_id
        }
