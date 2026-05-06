import os
from app.agents.router import run_agent
from app.rag.loader import ingest_course_pdfs
from app.rag.vector_store import build_vector_db, get_vector_store
from app.config import Config


def setup_vector_db():
    """Ingère les PDFs et construit la base vectorielle si elle n'existe pas."""
    
    # Vérifie si la base existe déjà
    if os.path.exists(Config.VECTOR_STORE_DIR) and os.listdir(Config.VECTOR_STORE_DIR):
        print("✅ Base vectorielle existante détectée. Chargement...")
        return get_vector_store()
    
    print("📚 Première exécution : ingestion des PDFs en cours...")
    chunks = ingest_course_pdfs()
    
    if not chunks:
        print("⚠️  Aucun PDF trouvé dans data/pdfs/. Placez vos cours puis relancez.")
        return None
    
    print(f"🔨 Construction de la base vectorielle ({len(chunks)} chunks)...")
    vector_db = build_vector_db(chunks)
    print("✅ Base vectorielle créée avec succès !")
    return vector_db


def run_cli():
    """Interface CLI en boucle pour interagir avec l'agent."""
    
    print("=" * 60)
    print("🤖  AI Personal Agent — BIHAR ESTIA")
    print("=" * 60)
    print("Commandes disponibles :")
    print("  'quitter' ou 'exit' → Arrêter l'agent")
    print("  'reset' → Effacer la mémoire de conversation")
    print("=" * 60)
    
    # Initialisation de la base vectorielle
    setup_vector_db()
    
    print("\n✅ Agent prêt ! Posez votre question.\n")
    
    while True:
        try:
            user_input = input("Vous : ").strip()
        except KeyboardInterrupt:
            print("\n👋 Au revoir !")
            break
        
        if not user_input:
            continue
        
        if user_input.lower() in ["quitter", "exit", "quit"]:
            print("👋 Au revoir !")
            break
        
        if user_input.lower() == "reset":
            from app.memory.storage import clear_memory
            clear_memory()
            continue
        
        print("\n⏳ Traitement en cours...\n")
        response = run_agent(user_input)
        
        print(f"\n🤖 Agent :\n{response}\n")
        print("-" * 60)


if __name__ == "__main__":
    run_cli()