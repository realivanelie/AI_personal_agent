from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.config import Config

def get_splitter():
    """Retourne le splitter de texte configuré."""
    return RecursiveCharacterTextSplitter(
        chunk_size=Config.CHUNK_SIZE,
        chunk_overlap=Config.CHUNK_OVERLAP,
        separators=["\n\n", "\n", ".", " ", ""]
    )

def split_documents(documents):
    """Découpe une liste de documents en chunks."""
    splitter = get_splitter()
    chunks = splitter.split_documents(documents)
    print(f" {len(documents)} pages → {len(chunks)} chunks")
    return chunks