"""
Tests unitaires : app/rag/splitter.py

Teste le découpage de documents sans dépendances externes.
"""
import pytest
from langchain_core.documents import Document
from app.rag.splitter import get_splitter, split_documents
from app.config import Config


# ---------------------------------------------------------------------------
# get_splitter
# ---------------------------------------------------------------------------

class TestGetSplitter:

    def test_returns_splitter_instance(self):
        splitter = get_splitter()
        assert splitter is not None

    def test_chunk_size_matches_config(self):
        splitter = get_splitter()
        assert splitter._chunk_size == Config.CHUNK_SIZE

    def test_chunk_overlap_matches_config(self):
        splitter = get_splitter()
        assert splitter._chunk_overlap == Config.CHUNK_OVERLAP

    def test_separators_are_set(self):
        splitter = get_splitter()
        assert splitter._separators is not None
        assert len(splitter._separators) > 0


# ---------------------------------------------------------------------------
# split_documents
# ---------------------------------------------------------------------------

class TestSplitDocuments:

    def _make_doc(self, content: str, source: str = "test.pdf") -> Document:
        return Document(page_content=content, metadata={"source": source})

    def test_single_short_doc_returns_one_chunk(self):
        doc = self._make_doc("Texte court.")
        chunks = split_documents([doc])
        assert len(chunks) >= 1

    def test_long_doc_is_split_into_multiple_chunks(self):
        long_text = "Mot " * 600  # ~2400 tokens, > CHUNK_SIZE=1000
        doc = self._make_doc(long_text)
        chunks = split_documents([doc])
        assert len(chunks) > 1

    def test_chunks_respect_max_size(self):
        long_text = "Mot " * 600
        doc = self._make_doc(long_text)
        chunks = split_documents([doc])
        for chunk in chunks:
            assert len(chunk.page_content) <= Config.CHUNK_SIZE * 2  # tolérance caractères

    def test_metadata_preserved_in_chunks(self):
        doc = self._make_doc("Contenu du cours.", source="cours_ml.pdf")
        chunks = split_documents([doc])
        for chunk in chunks:
            assert chunk.metadata.get("source") == "cours_ml.pdf"

    def test_empty_list_returns_empty_list(self):
        result = split_documents([])
        assert result == []

    def test_multiple_docs_all_chunked(self):
        docs = [
            self._make_doc("Premier document. " * 100, "doc1.pdf"),
            self._make_doc("Deuxième document. " * 100, "doc2.pdf"),
        ]
        chunks = split_documents(docs)
        sources = {c.metadata["source"] for c in chunks}
        assert "doc1.pdf" in sources
        assert "doc2.pdf" in sources

    def test_chunk_content_not_empty(self):
        doc = self._make_doc("Contenu non vide pour le test.")
        chunks = split_documents([doc])
        for chunk in chunks:
            assert chunk.page_content.strip() != ""
