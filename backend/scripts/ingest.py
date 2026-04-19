import os
import sys
import time
import chromadb
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, StorageContext, Settings
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.llms.google_genai import GoogleGenAI
from llama_index.embeddings.google_genai import GoogleGenAIEmbedding
from dotenv import load_dotenv

# Always resolve paths relative to backend/, regardless of where this script is called from
BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(BACKEND_DIR)

load_dotenv(os.path.join(BACKEND_DIR, ".env"))

api_key = os.getenv("GEMINI_API_KEY")
Settings.llm = GoogleGenAI(model="gemini-2.0-flash", api_key=api_key)
Settings.embed_model = GoogleGenAIEmbedding(model_name="models/text-embedding-004", api_key=api_key)

DB_PATH = "data/vector_db"
DOCS_DIR = "data/guidelines"


def ingest_safely():
    # Filter out non-PDF files like .gitkeep
    pdf_files = [
        f for f in os.listdir(DOCS_DIR)
        if f.lower().endswith(".pdf")
    ] if os.path.exists(DOCS_DIR) else []

    if not pdf_files:
        print(f"No PDFs found in {DOCS_DIR}. Add your MoH guideline PDFs and retry.")
        return

    print(f"Found {len(pdf_files)} PDF(s): {pdf_files}")
    print("Loading documents...")

    documents = SimpleDirectoryReader(
        DOCS_DIR,
        required_exts=[".pdf"]
    ).load_data()

    print(f"Loaded {len(documents)} pages total.")

    db = chromadb.PersistentClient(path=DB_PATH)
    chroma_collection = db.get_or_create_collection("moh_guidelines")

    # Check if already ingested
    existing = chroma_collection.count()
    if existing > 0:
        print(f"Vector DB already has {existing} chunks. Skipping re-ingestion.")
        print("To re-ingest, delete the data/vector_db folder and run again.")
        return

    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    batch_size = 20
    total_batches = (len(documents) + batch_size - 1) // batch_size

    for i in range(0, len(documents), batch_size):
        batch = documents[i:i + batch_size]
        batch_num = i // batch_size + 1
        print(f"\nProcessing batch {batch_num}/{total_batches} (pages {i+1} to {i+len(batch)})...")

        success = False
        while not success:
            try:
                VectorStoreIndex.from_documents(
                    batch,
                    storage_context=storage_context,
                    show_progress=True
                )
                success = True
                if batch_num < total_batches:
                    print(f"Batch {batch_num} done. Waiting 15s to respect API quota...")
                    time.sleep(15)
            except Exception as e:
                if "429" in str(e) or "ResourceExhausted" in str(e):
                    print("Rate limit hit. Waiting 60s...")
                    time.sleep(60)
                else:
                    print(f"Unexpected error: {e}")
                    sys.exit(1)

    final_count = chroma_collection.count()
    print(f"\nDone! Vector DB now has {final_count} chunks ready for RAG queries.")


if __name__ == "__main__":
    ingest_safely()
