import os
from app.config import Config
from app.rag.loader import ingest_course_pdfs
from app.rag.vector_store import build_vector_db
from langchain_community.chat_models import ChatOllama
from langchain.chains import RetrievalQA

def start_diagnostic():
    print(" --- DIAGNOSTIC RAG BIHAR ---")
    
    # ÉTAPE 1 : Chargement
    chunks = ingest_course_pdfs()
    print(f"1. Nombre de chunks créés : {len(chunks)}")
    if len(chunks) == 0:
        print(" STOP : Aucun texte n'a été extrait des PDF.")
        return

    # ÉTAPE 2 : Création Vector DB
    print("2. Création de la base vectorielle...")
    vector_db = build_vector_db(chunks)
    
    # ÉTAPE 3 : Test de recherche (Le coeur du problème)
    print(f"3. Test de recherche de similarité pour '{test_query}'.")
    results = vector_db.similarity_search(test_query, k=2)
    
    if not results:
        print(" STOP : La recherche de similarité ne renvoie rien.")
        return
    else:
        print(f" Succès : {len(results)} extraits trouvés.")
        print(f" Premier extrait trouvé : {results[0].page_content[:150]}...")

    # ÉTAPE 4 : Test Ollama
    print("4. Envoi à Ollama (Llama3)...")
    llm = ChatOllama(model=Config.LLM_MODEL, base_url=Config.OLLAMA_BASE_URL)
    
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=vector_db.as_retriever()
    )
    
    res = qa_chain.invoke("D'après les documents, quels sont les thèmes principaux ?")
    print("\n RÉPONSE FINALE :")
    print(res["result"])

if __name__ == "__main__":
    start_diagnostic()