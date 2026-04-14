import os
from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI


class ethioRAG:
     def __init__(self, persist_dir: str = "../data/vector_db"):
        self.persist_dir = Path(persist_dir)
        self.embeddings = HuggingFaceEmbeddings(model_name="intfloat/multilingual-e5-large")
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash-exp",
            temperature=0,
            google_api_key=os.getenv("GOOGLE_API_KEY")
        )
        self.vectorstore = None
        