from langchain_huggingface import HuggingFaceEmbeddings

def get_embeddings():
    """Retourne le modèle d'embeddings local HuggingFace."""
    return HuggingFaceEmbeddings(
        model_name="all-MiniLM-L6-v2",
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True}
    )