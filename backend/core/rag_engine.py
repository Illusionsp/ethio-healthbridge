import os
import json
import time
from pathlib import Path
from typing import List, Dict, Any

import numpy as np
from PyPDF2 import PdfReader
import google.generativeai as genai


class EthioRAG:
    def __init__(
        self,
        index_path: str = "backend/data/vector_db/moh_index.json",
        gemini_model: str = "gemini-1.5-flash",
        embedding_model: str = "models/text-embedding-004",
    ):
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY is missing. Set it in your environment.")

        genai.configure(api_key=api_key)
        self.llm = genai.GenerativeModel(gemini_model)
        self.embedding_model = embedding_model

        self.index_path = Path(index_path)
        self.index_path.parent.mkdir(parents=True, exist_ok=True)

        self.index: List[Dict[str, Any]] = []
        if self.index_path.exists():
            self._load_index()

   
    def load_pdf_pages(self, pdf_path: str):
        reader = PdfReader(pdf_path)
        pages = []

        for i, page in enumerate(reader.pages):
            text = page.extract_text() or ""
            text = " ".join(text.split())
            if text:
             pages.append({"page_num": i + 1, "text": text})

        return pages

    @staticmethod
    def split_text(text: str, chunk_size: int = 700, overlap: int = 120) -> List[str]:
        chunks = []
        start = 0
        n = len(text)

        while start < n:
            end = min(start + chunk_size, n)
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            if end == n:
                break
            start += chunk_size - overlap

        return chunks
    
    def embed_text(self, text: str) -> np.ndarray:
        # Retry once for transient API/network issues
        for attempt in range(2):
            try:
                result = genai.embed_content(
                    model=self.embedding_model,
                    content=text,
                    task_type="retrieval_document",
                )
                vector = np.array(result["embedding"], dtype=np.float32)
                return vector
            except Exception:
                if attempt == 1:
                    raise
                time.sleep(1.2)

        raise RuntimeError("Embedding failed unexpectedly.")

    def index_guidelines(self, pdf_path: str):
        print("Loading PDF...")
        pages = self.load_pdf_pages(pdf_path)
        print(f"Total extracted pages: {len(pages)}")

        # emergency triage + common illnesses slice
        selected_pages = pages[8:18] + pages[15:35]
        print(f"Selected pages for Day-1 indexing: {len(selected_pages)}")

        new_index = []
        chunk_counter = 0

        for page in selected_pages:
            page_num = page["page_num"]
            chunks = self.split_text(page["text"], chunk_size=700, overlap=120)

            for chunk in chunks:
                emb = self.embed_text(chunk)
                new_index.append(
                    {
                        "id": f"p{page_num}_c{chunk_counter}",
                        "page": page_num,
                        "text": chunk,
                        "embedding": emb.tolist(),
                    }
                )
                chunk_counter += 1

        self.index = new_index
        self._save_index()
        print(f"Indexing done: {len(self.index)} chunks saved to {self.index_path}")

    def retrieve(self, question: str, k: int = 4) -> List[Dict[str, Any]]:
        if not self.index:
            raise ValueError("Index is empty. Run index_guidelines() first.")

        q_emb = self.embed_text(question)

        scored = []
        q_norm = np.linalg.norm(q_emb) + 1e-8

        for item in self.index:
            d_emb = np.array(item["embedding"], dtype=np.float32)
            score = float(np.dot(q_emb, d_emb) / (q_norm * (np.linalg.norm(d_emb) + 1e-8)))
            scored.append((score, item))

        scored.sort(key=lambda x: x[0], reverse=True)
        top = [item for _, item in scored[:k]]
        return top

    def query(self, question: str, k: int = 4) -> Dict[str, Any]:
        docs = self.retrieve(question, k=k)
        context_blocks = []

        for d in docs:
            context_blocks.append(f"[Page {d['page']}] {d['text']}")

        context = "\n\n".join(context_blocks)

        prompt = f"""
You are an Ethiopian clinical assistant.

STRICT RULES:
1) Answer only from the CONTEXT.
2) Answer in clear Amharic.
3) If context is not enough, say exactly: "አልታወቀም"
4) Keep advice safe and practical.
5) For emergency danger signs, clearly tell user to seek urgent care.

CONTEXT:
{context}

QUESTION:
{question}
""".strip()

        response = self.llm.generate_content(prompt)

        return {
            "answer": (response.text or "").strip(),
            "sources": [{"page": d["page"], "id": d["id"]} for d in docs],
        }

    
    def _save_index(self):
        with open(self.index_path, "w", encoding="utf-8") as f:
            json.dump(self.index, f, ensure_ascii=False)

    def _load_index(self):
        with open(self.index_path, "r", encoding="utf-8") as f:
            self.index = json.load(f)


if __name__ == "__main__":
    rag = EthioRAG()

    # Day-1 index build (run once, then comment out)
    rag.index_guidelines("backend/data/guidelines/Ethiopian Primary care clinical guideline 2017 - DIGITAL final draft (1).pdf")

    tests = ["ራሴን ያመኛል", "ትኩሳት አለኝ", "የመተንፈስ ችግር አለኝ"]
    for q in tests:
        res = rag.query(q, k=4)
        print("\nQ:", q)
        print("A:", res["answer"])
        print("Sources:", res["sources"])