import os
from pathlib import Path
import chromadb
from chromadb.utils import embedding_functions
from pypdf import PdfReader
from google import genai

class EthioRAG:
    def __init__(self, path_dir="backend/data/vector_db"):

        self.path_dir = path_dir

        self.client_gemini = genai.Client(
            api_key=os.getenv("GOOGLE_API_KEY")
        )


        self.client = chromadb.PersistentClient(path=path_dir)

        self.embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="intfloat/multilingual-e5-large"
        )

        self.collection = self.client.get_or_create_collection(
            name="ethio_health",
            embedding_function=self.embedding_function
        )

    def load_pdf(self, pdf_path):
        reader = PdfReader(pdf_path)
        texts = []

        for i, page in enumerate(reader.pages):
            text = page.extract_text()
            if text:
                texts.append((f"page_{i}", text))

        return texts
