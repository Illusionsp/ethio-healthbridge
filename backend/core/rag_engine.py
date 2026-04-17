import os
import chromadb
from llama_index.core import VectorStoreIndex, StorageContext, Settings
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.llms.gemini import Gemini
from llama_index.embeddings.gemini import GeminiEmbedding
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
    
# 2. FIXED: Path consistency
DB_PATH = "data/vector_db"

def get_db_collection():
    os.makedirs(DB_PATH, exist_ok=True)
    db = chromadb.PersistentClient(path=DB_PATH)
    return db.get_or_create_collection("moh_guidelines")

def query_medical_guidelines(query_text: str) -> str:
    print(f"🔍 RAG query: '{query_text}'")
    
    # --- 🛡️ SAFETY CHECK: BLANK AUDIO ---
    if not query_text or query_text.strip() == "":
        return "እባክዎ ጥያቄዎን በድጋሚ ይናገሩ። ድምፅዎ አልተሰማም።"
    
    # --- 👋 GREETINGS CHECK ---
    # Convert input to lowercase and remove spaces to catch "hi", "Hi", "  hi  ", etc.
    user_input = query_text.lower().strip()
    greetings = ["hi", "hello", "hey", "ሰላም", "ጤና ይስጥልኝ"]
    
    if user_input in greetings:
        return "ጤና ይስጥልኝ! እኔ Ethio-HealthBridge ነኝ። በኢትዮጵያ ጤና ሚኒስቴር መመሪያዎች ላይ ተመስርቼ ስለ ጤናዎ መረጃ በመስጠት ልረዳዎ እችላለሁ። እንዴት ልርዳዎ?"
    # ---------------------------

    try:
        collection = get_db_collection()
        
        # Fallback if DB is empty (First Run)
        if collection.count() == 0:
            return _basic_llm_response(query_text)
            
        vector_store = ChromaVectorStore(chroma_collection=collection)
        storage_context = StorageContext.from_defaults(vector_store=vector_store)
        index = VectorStoreIndex.from_vector_store(vector_store, storage_context=storage_context)
        
        query_engine = index.as_query_engine(similarity_top_k=3)
        response = query_engine.query(query_text)
        
        source_texts = "\n\n".join([f"Source (Score: {node.score}):\n{node.text}" for node in response.source_nodes])
        
        # --- NEW METADATA EXTRACTION INSERTED HERE ---
        sources = []
        for node in response.source_nodes:
            fname = node.metadata.get('file_name', 'MoH Document')
            page = node.metadata.get('page_label', 'N/A')
            sources.append(f"{fname} (ገጽ {page})")

        unique_sources = list(set(sources))
        source_string = ", ".join(unique_sources)
        # ---------------------------------------------
        
        amharic_prompt = f"""
        You are 'Ethio-HealthBridge', a highly professional Medical AI for Ethiopia.
        Your sole task is to formulate a culturally respectful Amharic response based ONLY on the retrieved context.
        
        STRICT RULES:
        1. NO HALLUCINATION: You must ONLY use the information provided in the context below. 
        2. EXPLICIT REFERENCING: Explicitly state "በኢትዮጵያ ጤና ሚኒስቴር መመሪያ መሰረት ({source_string})፦".
        3. AMHARIC MORPHOLOGY: Use flawless formal Amharic.
        4. ACTIVE TRIAGE (INCOMPLETE SYMPTOMS): If the user's symptoms are too broad to pinpoint a single disease (e.g., just "ቁርጥማት" and "ብርድ ብርድ ማለት"), DO NOT just say you can't find it. State that these symptoms match multiple illnesses, and explicitly ASK the user to provide more symptoms to narrow it down. 
           Example: "በኢትዮጵያ ጤና ሚኒስቴር መመሪያ መሰረት፣ እነዚህ ምልክቶች ለተለያዩ በሽታዎች ሊሆኑ ይችላሉ። በሽታውን በተሻለ ለመለየት፣ እባክዎ ሌሎች ተጨማሪ ምልክቶች ካሉዎት (ለምሳሌ፡ ትኩሳት ወይም ማስመለስ) ይንገሩኝ።"
        5. IF COMPLETELY UNCERTAIN: If the context truly does not answer the question at all, say "ይቅርታ፣ በዚህ ጉዳይ ላይ በጤና ሚኒስቴር መመሪያ ውስጥ መረጃ አላገኘሁም።"
        
        SYMPTOM TRANSLATION EXAMPLES:
        - "ውጋት" -> sharp body or chest pain
        - "ቁርጠት" -> cramps or abdominal pain
        - "ማዞር" -> dizziness or vertigo
        - "ልቤን ይሞረሙረኛል" -> nausea or heartburn
        - "ምች" -> sudden febrile illness, sunstroke, or viral infection
        - "የከንፈር ምች" -> fever blisters or herpes labialis
        - "ቁርጥማት" -> severe joint pain, bone aches, rheumatism, or myalgia
        - "ብርድ ብርድ ማለት" -> chills or rigors
        
        USER'S ORIGINAL QUERY:
        {query_text}
        
        RETRIEVED MoH CONTEXT:
        {source_texts}
        
        Please provide the final Amharic response now:
        """
        final_am_response = Settings.llm.complete(amharic_prompt)
        return str(final_am_response)
        
    except Exception as e:
        print(f"RAG Error: {e}")
        return "ይቅርታ፣ አሁን ላይ መረጃ ማግኘት አልቻልኩም። እባክዎ ወደ ጤና ተቋም ይሂዱ።"

def _basic_llm_response(query_text: str) -> str:
    return "የሕክምና መመሪያ ማከማቻው በአሁኑ ጊዜ ባዶ ነው። አፋጣኝ ሕክምና የሚያስፈልግዎ ከሆነ ወደ ጥቁር አንበሳ (Black Lion) ወይም በአቅራቢያዎ ወደሚገኝ ጤና ጣቢያ ይሂዱ። ድንገተኛ: 912"

if __name__ == "__main__":
    print(query_medical_guidelines("ራስ ምታት እና ትኩሳት"))