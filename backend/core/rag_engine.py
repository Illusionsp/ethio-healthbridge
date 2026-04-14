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

        # Same spirit as your plan: emergency triage + common illnesses slice
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

   