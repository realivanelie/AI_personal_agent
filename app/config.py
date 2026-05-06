import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Paramètres Ollama (Local)
    LLM_MODEL = "qwen2.5-coder:7b"
    OLLAMA_BASE_URL = "http://localhost:11434"
    
    # Chemins
    DATA_DIR = "data/pdfs"
    VECTOR_STORE_DIR = "data/vector_store"
    
    # RAG
    CHUNK_SIZE = 1000
    CHUNK_OVERLAP = 150