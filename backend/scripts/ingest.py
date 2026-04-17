import os
import time
import chromadb
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, StorageContext, Settings
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.llms.gemini import Gemini
from llama_index.embeddings.gemini import GeminiEmbedding
from dotenv import load_dotenv

load_dotenv()

# Configuration
Settings.llm = Gemini(model_name="models/gemini-2.5-flash-lite")
Settings.embed_model = GeminiEmbedding(model_name="models/gemini-embedding-001")

DB_PATH = "data/vector_db"
DOCS_DIR = "data/guidelines"

def ingest_safely():
    if not os.path.exists(DOCS_DIR) or not os.listdir(DOCS_DIR):
        print(f"❌ Error: No PDFs found in {DOCS_DIR}.")
        return

    print(f"📄 Loading documents...")
    documents = SimpleDirectoryReader(DOCS_DIR).load_data()
    
    # Initialize Chroma
    db = chromadb.PersistentClient(path=DB_PATH)
    chroma_collection = db.get_or_create_collection("moh_guidelines")
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    # Break documents into smaller batches of 20 pages
    batch_size = 20
    for i in range(0, len(documents), batch_size):
        batch = documents[i:i + batch_size]
        print(f"🧠 Processing batch {i//batch_size + 1} ({i} to {i+len(batch)})...")
        
        success = False
        while not success:
            try:
                # Add this specific batch to the index
                VectorStoreIndex.from_documents(
                    batch,
                    storage_context=storage_context,
                    show_progress=True
                )
                success = True
                print(f"✅ Batch {i//batch_size + 1} saved. Resting for 15 seconds...")
                time.sleep(15) # Wait between batches to keep the quota happy
            except Exception as e:
                if "429" in str(e) or "ResourceExhausted" in str(e):
                    print("⚠️ Rate limit hit! Sleeping for 60 seconds...")
                    time.sleep(60)
                else:
                    print(f"❌ Unexpected Error: {e}")
                    return

    print(f"🚀 MISSION ACCOMPLISHED! Your AI now has a medical brain.")

if __name__ == "__main__":
    ingest_safely()