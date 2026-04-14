import os
from pathlib import Path
import chromadb
from chromadb.utils import embedding_functions
from pypdf import PdfReader
import google.generativeai as genai

class EthioRAG:
    def __init__(self, path_dir="backend/data/vector_db"):
        self.path_dir = path_dir
        