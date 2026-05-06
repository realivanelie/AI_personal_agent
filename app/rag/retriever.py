from app.rag.vector_store import get_vector_store

def get_retriever(k: int = 4):
    """
    Retourne un retriever depuis la base vectorielle persistée.
    k = nombre de chunks renvoyés par requête.
    """
    vector_store = get_vector_store()
    retriever = vector_store.as_retriever(
        search_type="similarity",
        search_kwargs={"k": k}
    )
    return retriever

def retrieve_context(query: str, k: int = 4) -> str:
    """
    Récupère le contexte pertinent pour une question donnée.
    Retourne un string formaté prêt à injecter dans un prompt.
    """
    retriever = get_retriever(k=k)
    docs = retriever.invoke(query)
    
    if not docs:
        return "Aucun contexte trouvé dans les cours."
    
    context_parts = []
    for i, doc in enumerate(docs, 1):
        source = doc.metadata.get("source", "Inconnu").split("/")[-1]
        page = doc.metadata.get("page", "?")
        context_parts.append(
            f"[Extrait {i} - {source}, p.{page}]\n{doc.page_content}"
        )
    
    return "\n\n---\n\n".join(context_parts)