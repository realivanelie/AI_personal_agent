import os
from app.config import Config
from app.rag.loader import ingest_course_pdfs
from app.rag.vector_store import build_vector_db, get_vector_store
from langchain_community.chat_models import ChatOllama
from langchain.chains import RetrievalQA


def run_local_test():
    print("🏠 Démarrage du test RAG 100% LOCAL (Ollama)...")

    # 1. Chargement de la base de données
    if not os.path.exists(Config.VECTOR_STORE_DIR):
        print("📁 Ingestion des fichiers PDF...")
        chunks = ingest_course_pdfs()
        vector_db = build_vector_db(chunks)
    else:
        print("✅ Utilisation de la base vectorielle existante.")
        vector_db = get_vector_store()

    # 2. Setup Ollama
    print(f"🤖 Connexion à Ollama ({Config.LLM_MODEL})...")
    llm = ChatOllama(
        model=Config.LLM_MODEL,
        base_url=Config.OLLAMA_BASE_URL,
        temperature=0.3
    )

    # 3. Chaîne RAG
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=vector_db.as_retriever(search_kwargs={"k": 3})
    )

    # 4. Question
    query = "Fais-moi un résumé structuré du cours de deep learning avec les 3 points les plus importants en français."
    print(f"❓ Question : {query}")
    
    try:
        response = qa_chain.invoke(query)
        print("\n📝 RÉPONSE OLLAMA :")
        print(response["result"])
    except Exception as e:
        print(f"❌ Erreur : {e}. Vérifie que le service Ollama est bien lancé !")

if __name__ == "__main__":
    run_local_test()