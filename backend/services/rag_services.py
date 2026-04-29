# app/services/rag_service.py

from typing import List, Dict
import chromadb
from chromadb.utils import embedding_functions

# Connect to the same persistent ChromaDB folder [web:16][web:108]
client = chromadb.PersistentClient(path="chroma_db")
collection = client.get_or_create_collection(name="ephcg_amharic")

# Same embedder as in ingest_ephcg.py
embedder = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

def retrieve_context(query: str, top_k: int = 3) -> List[Dict]:
    """
    Use ChromaDB to find the most similar EPHCG chunks to the user query.
    """
    query_emb = embedder([query])[0]

    results = collection.query(
        query_embeddings=[query_emb],
        n_results=top_k,
    )

    docs: List[Dict] = []
    for i, text in enumerate(results["documents"][0]):
        docs.append(
            {
                "id": results["ids"][0][i],
                "section": results["metadatas"][0][i].get("section", ""),
                "text": text,
            }
        )
    return docs

def build_prompt_amharic(query: str, context_docs: List[Dict]) -> str:
    """
    Build an Amharic prompt using retrieved guideline chunks
    (for future LLM use).
    """
    context_blocks = []
    for i, doc in enumerate(context_docs, start=1):
        context_blocks.append(
            f"[ምንጭ {i} - {doc['section']}]\n{doc['text']}\n"
        )

    context_text = "\n\n".join(context_blocks)

    prompt = f"""
እርስዎ የመጀመሪያ ደረጃ ጤና አገልግሎት አማርኛ ረዳት ነዎት።
ምላሽዎን በታች ያሉትን የመመሪያ ጽሁፎች ብቻ ላይ ያቆሙ።
ከእነዚህ ውጭ ትምክህት አትጨምሩ፣ ምንም ነገር አታፍኑ።

[ጥያቄ]
{query}

[መመሪያ ምንጮች]
{context_text}

በአጭሩ ግልጽና ተረዳጋ መልኩ መመሪያ ይስጡ።
ከሆነ የአደጋ ምልክቶችን ያስታውቁና ወደ የጤና ጣቢያ ወይም 912 እንዲደውሉ ይመክሩ።
"""
    return prompt