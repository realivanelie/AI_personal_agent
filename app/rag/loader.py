import os
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.config import Config

def ingest_course_pdfs():
    documents = []
    # On liste tous les fichiers du dossier
    all_files = os.listdir(Config.DATA_DIR)
    
    print(f" Analyse du dossier : {len(all_files)} fichiers trouvés.")
    
    for file in all_files:
        path = os.path.join(Config.DATA_DIR, file)
        try:
            # Traitement des PDFs
            if file.endswith('.pdf'):
                loader = PyPDFLoader(path)
                data = loader.load()
                documents.extend(data)
                print(f" Chargé (PDF) : {file} ({len(data)} pages)")
            
            # Traitement des fichiers texte, Markdown et SQL
            elif file.endswith(('.md', '.sql', '.txt')):
                loader = TextLoader(path, encoding='utf-8')
                data = loader.load()
                documents.extend(data)
                print(f" Chargé (Texte/Code) : {file}")
                
        except Exception as e:
            print(f" Erreur sur {file} : {e}")

    if not documents:
        return []

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=Config.CHUNK_SIZE,
        chunk_overlap=Config.CHUNK_OVERLAP
    )
    chunks = splitter.split_documents(documents)
    return chunks