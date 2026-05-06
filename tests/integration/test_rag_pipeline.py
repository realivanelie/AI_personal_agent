"""
Tests d'intégration : pipeline RAG complet
(loader → splitter → embeddings → vector_store → retriever)

Ces tests utilisent de vrais composants LangChain/ChromaDB/HuggingFace
mais fonctionnent sur des données temporaires en mémoire.
Aucun appel Ollama.

Marqués @pytest.mark.integration — lancez avec :
    pytest -m integration
"""
import pytest
import tempfile
import os
from langchain_core.documents import Document


pytestmark = pytest.mark.integration


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def sample_docs():
    """Faux documents représentatifs du domaine ML."""
    return [
        Document(
            page_content=(
                "La régression logistique est un algorithme de classification supervisée. "
                "Elle utilise la fonction sigmoïde pour modéliser des probabilités. "
                "La fonction de coût est la cross-entropie binaire. "
                "L'optimisation se fait par descente de gradient."
            ),
            metadata={"source": "ml_chapter1.pdf", "page": 1}
        ),
        Document(
            page_content=(
                "Les réseaux de neurones convolutifs (CNN) sont utilisés pour la vision par ordinateur. "
                "Ils comprennent des couches de convolution, de pooling et de fully-connected. "
                "Le transfer learning permet de réutiliser des poids pré-entraînés comme ResNet ou VGG."
            ),
            metadata={"source": "dl_cnn.pdf", "page": 3}
        ),
        Document(
            page_content=(
                "Le MLOps désigne l'ensemble des pratiques pour déployer des modèles en production. "
                "Il inclut le versioning de données, le monitoring, la CI/CD et la reproductibilité. "
                "Des outils comme MLflow, DVC et Airflow sont couramment utilisés."
            ),
            metadata={"source": "mlops.pdf", "page": 1}
        ),
        Document(
            page_content=(
                "Les séries temporelles sont des données ordonnées dans le temps. "
                "Les modèles ARIMA, LSTM et Prophet sont utilisés pour les prévisions. "
                "La stationnarité est une propriété clé avant toute modélisation."
            ),
            metadata={"source": "time_series.pdf", "page": 2}
        ),
    ]


@pytest.fixture(scope="module")
def vector_store_from_docs(sample_docs):
    """Construit un ChromaDB en mémoire à partir des docs de test."""
    from app.rag.splitter import split_documents
    from app.rag.embeddings import get_embeddings
    from langchain_community.vectorstores import Chroma

    chunks = split_documents(sample_docs)
    embeddings = get_embeddings()

    with tempfile.TemporaryDirectory() as tmpdir:
        store = Chroma.from_documents(
            documents=chunks,
            embedding=embeddings,
            persist_directory=tmpdir
        )
        yield store


# ---------------------------------------------------------------------------
# Tests splitter dans le pipeline
# ---------------------------------------------------------------------------

class TestPipelineChunking:

    def test_documents_are_chunked(self, sample_docs):
        from app.rag.splitter import split_documents
        chunks = split_documents(sample_docs)
        assert len(chunks) >= len(sample_docs)

    def test_all_sources_present_in_chunks(self, sample_docs):
        from app.rag.splitter import split_documents
        chunks = split_documents(sample_docs)
        sources = {c.metadata.get("source") for c in chunks}
        assert "ml_chapter1.pdf" in sources
        assert "dl_cnn.pdf" in sources
        assert "mlops.pdf" in sources

    def test_no_empty_chunks(self, sample_docs):
        from app.rag.splitter import split_documents
        chunks = split_documents(sample_docs)
        for chunk in chunks:
            assert chunk.page_content.strip() != ""


# ---------------------------------------------------------------------------
# Tests embeddings
# ---------------------------------------------------------------------------

class TestEmbeddings:

    def test_embeddings_load(self):
        from app.rag.embeddings import get_embeddings
        embeddings = get_embeddings()
        assert embeddings is not None

    def test_embed_single_text(self):
        from app.rag.embeddings import get_embeddings
        embeddings = get_embeddings()
        vector = embeddings.embed_query("Qu'est-ce que le gradient descent ?")
        assert isinstance(vector, list)
        assert len(vector) == 384  # all-MiniLM-L6-v2 → 384 dimensions

    def test_embed_documents(self):
        from app.rag.embeddings import get_embeddings
        embeddings = get_embeddings()
        vectors = embeddings.embed_documents(["Texte A", "Texte B"])
        assert len(vectors) == 2
        assert all(len(v) == 384 for v in vectors)


# ---------------------------------------------------------------------------
# Tests vector store + retrieval
# ---------------------------------------------------------------------------

class TestVectorStoreRetrieval:

    def test_similarity_search_returns_docs(self, vector_store_from_docs):
        results = vector_store_from_docs.similarity_search("CNN convolution pooling", k=2)
        assert len(results) > 0

    def test_relevant_doc_retrieved_for_cnn_query(self, vector_store_from_docs):
        results = vector_store_from_docs.similarity_search("réseau de neurones convolutifs", k=2)
        contents = " ".join(r.page_content for r in results)
        # Le chunk CNN doit apparaître dans les premiers résultats
        assert "convol" in contents.lower() or "cnn" in contents.lower()

    def test_relevant_doc_retrieved_for_mlops_query(self, vector_store_from_docs):
        results = vector_store_from_docs.similarity_search("déploiement modèle MLOps CI/CD", k=2)
        contents = " ".join(r.page_content for r in results)
        assert "mlops" in contents.lower() or "déployer" in contents.lower() or "production" in contents.lower()

    def test_retriever_with_k_parameter(self, vector_store_from_docs):
        retriever = vector_store_from_docs.as_retriever(search_kwargs={"k": 3})
        docs = retriever.invoke("régression logistique")
        assert len(docs) <= 3

    def test_metadata_preserved_after_retrieval(self, vector_store_from_docs):
        results = vector_store_from_docs.similarity_search("séries temporelles ARIMA", k=1)
        assert results[0].metadata.get("source") is not None


# ---------------------------------------------------------------------------
# Tests retrieve_context (format de sortie du retriever)
# ---------------------------------------------------------------------------

class TestRetrieveContextFormat:

    def test_retrieve_context_returns_string(self, vector_store_from_docs, monkeypatch):
        """Patche get_vector_store pour utiliser notre store de test."""
        import app.rag.retriever as retriever_mod
        monkeypatch.setattr(retriever_mod, "get_vector_store", lambda: vector_store_from_docs)

        from app.rag.retriever import retrieve_context
        context = retrieve_context("régression logistique")
        assert isinstance(context, str)

    def test_retrieve_context_contains_source_info(self, vector_store_from_docs, monkeypatch):
        import app.rag.retriever as retriever_mod
        monkeypatch.setattr(retriever_mod, "get_vector_store", lambda: vector_store_from_docs)

        from app.rag.retriever import retrieve_context
        context = retrieve_context("CNN deep learning")
        assert "Extrait" in context

    def test_retrieve_context_no_docs_returns_fallback(self, monkeypatch):
        """Si la base est vide, retourne le message de fallback."""
        from unittest.mock import MagicMock
        import app.rag.retriever as retriever_mod

        mock_store = MagicMock()
        mock_retriever = MagicMock()
        mock_retriever.invoke.return_value = []
        mock_store.as_retriever.return_value = mock_retriever
        monkeypatch.setattr(retriever_mod, "get_vector_store", lambda: mock_store)

        from app.rag.retriever import retrieve_context
        context = retrieve_context("question sans résultats")
        assert "Aucun contexte" in context
