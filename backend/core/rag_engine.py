import os
import chromadb
from llama_index.core import VectorStoreIndex
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core import StorageContext, Settings
from llama_index.llms.gemini import Gemini
from llama_index.embeddings.gemini import GeminiEmbedding

try:
    # 1. FIXED: Upgraded to Gemini 2.5 Flash and changed "model" to "model_name"
    Settings.llm = Gemini(model_name="models/gemini-2.5-flash")
    Settings.embed_model = GeminiEmbedding(model_name="models/text-embedding-004")
except Exception as e:
    print(f"Warning: Could not initialize Gemini or Embedding Model. {e}")

# 2. FIXED: Path updated so it doesn't create nested backend/backend/data folders
DB_PATH = "data/vector_db"

def get_db_collection():
    os.makedirs(DB_PATH, exist_ok=True)
    db = chromadb.PersistentClient(path=DB_PATH)
    return db.get_or_create_collection("moh_guidelines")

def query_medical_guidelines(query_text: str) -> str:
    print(f"🔍 RAG query: {query_text}")
    try:
        collection = get_db_collection()
        
        # Fallback if DB is empty (First Run)
        if collection.count() == 0:
            return _basic_llm_response(query_text)
            
        vector_store = ChromaVectorStore(chroma_collection=collection)
        storage_context = StorageContext.from_defaults(vector_store=vector_store)
        index = VectorStoreIndex.from_vector_store(vector_store, storage_context=storage_context)
        
        query_engine = index.as_query_engine(similarity_top_k=5)
        response = query_engine.query(query_text)
        
        source_texts = "\n\n".join([f"Source (Score: {node.score}):\n{node.text}" for node in response.source_nodes])
        
        amharic_prompt = f"""
        You are 'Ethio-HealthBridge', a highly professional Medical AI for Ethiopia.
        Your sole task is to formulate a culturally respectful Amharic response based ONLY on the retrieved context.
        
        STRICT RULES:
        1. NO HALLUCINATION: You must ONLY use the information provided in the context below. 
        2. EXPLICIT REFERENCING: Explicitly state "በኢትዮጵያ ጤና ሚኒስቴር መመሪያ መሰረት".
        3. AMHARIC MORPHOLOGY: Use flawless formal Amharic.
        4. IF UNCERTAIN: If the context does not answer the question, say "ይቅርታ፣ በዚህ ጉዳይ ላይ በጤና ሚኒስቴር መመሪያ ውስጥ መረጃ አላገኘሁም።"
        
        SYMPTOM TRANSLATION EXAMPLES:
        - "ውጋት" -> sharp body or chest pain
        - "ቁርጠት" -> cramps or abdominal pain
        - "ማዞር" -> dizziness or vertigo
        - "ልቤን ይሞረሙረኛል" -> nausea or heartburn
        
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