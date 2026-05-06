from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from app.config import Config
import os

def get_embeddings():
    return HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

def build_vector_db(chunks):
    embeddings = get_embeddings()
    vector_db = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=Config.VECTOR_STORE_DIR
    )
    return vector_db

def get_vector_store():
    embeddings = get_embeddings()
    return Chroma(
        persist_directory=Config.VECTOR_STORE_DIR,
        embedding_function=embeddings
    )