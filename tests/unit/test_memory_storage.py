"""
Tests unitaires : app/memory/storage.py

Teste la mémoire de session sans dépendances externes (pas d'Ollama, pas de ChromaDB).
"""
import pytest
from unittest.mock import patch, MagicMock


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _fresh_memory_module():
    """
    Recharge le module storage avec une instance _memory vierge.
    Nécessaire car _memory est un singleton au niveau module.
    """
    import importlib
    import app.memory.storage as mod
    importlib.reload(mod)
    return mod


# ---------------------------------------------------------------------------
# save_exchange / get_history
# ---------------------------------------------------------------------------

class TestSaveAndGetHistory:

    def test_save_single_exchange(self):
        mod = _fresh_memory_module()
        mod.save_exchange("Qu'est-ce que le gradient descent ?", "Le gradient descent est...")
        history = mod.get_history()
        # 1 échange = 2 messages (human + assistant)
        assert len(history) == 2
        assert history[0]["role"] == "user"
        assert history[0]["content"] == "Qu'est-ce que le gradient descent ?"

    def test_history_preserves_ai_response(self):
        mod = _fresh_memory_module()
        mod.save_exchange("Question", "Réponse IA")
        history = mod.get_history()
        assert history[1]["role"] == "assistant"
        assert history[1]["content"] == "Réponse IA"

    def test_save_multiple_exchanges(self):
        mod = _fresh_memory_module()
        mod.save_exchange("Q1", "R1")
        mod.save_exchange("Q2", "R2")
        history = mod.get_history()
        assert len(history) == 4  # 2 human + 2 ai

    def test_history_order_is_chronological(self):
        mod = _fresh_memory_module()
        mod.save_exchange("Premier", "Réponse 1")
        mod.save_exchange("Deuxième", "Réponse 2")
        history = mod.get_history()
        assert history[0]["content"] == "Premier"
        assert history[2]["content"] == "Deuxième"

    def test_empty_history_returns_empty_list(self):
        mod = _fresh_memory_module()
        assert mod.get_history() == []


# ---------------------------------------------------------------------------
# clear_memory
# ---------------------------------------------------------------------------

class TestClearMemory:

    def test_clear_resets_history(self):
        mod = _fresh_memory_module()
        mod.save_exchange("Question", "Réponse")
        mod.clear_memory()
        assert mod.get_history() == []

    def test_clear_then_save_works(self):
        mod = _fresh_memory_module()
        mod.save_exchange("Ancienne question", "Ancienne réponse")
        mod.clear_memory()
        mod.save_exchange("Nouvelle question", "Nouvelle réponse")
        history = mod.get_history()
        assert len(history) == 2
        assert history[0]["content"] == "Nouvelle question"


# ---------------------------------------------------------------------------
# get_memory
# ---------------------------------------------------------------------------

class TestGetMemory:

    def test_get_memory_returns_object(self):
        mod = _fresh_memory_module()
        memory = mod.get_memory()
        assert memory is not None

    def test_get_memory_same_instance(self):
        """Le singleton doit retourner le même objet."""
        mod = _fresh_memory_module()
        assert mod.get_memory() is mod.get_memory()


# ---------------------------------------------------------------------------
# Window limit (k=10)
# ---------------------------------------------------------------------------

class TestWindowLimit:

    def test_window_keeps_last_10_exchanges(self):
        mod = _fresh_memory_module()
        for i in range(12):
            mod.save_exchange(f"Question {i}", f"Réponse {i}")
        history = mod.get_history()
        # k=10 → max 20 messages (10 human + 10 ai)
        assert len(history) <= 20
