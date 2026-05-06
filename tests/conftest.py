"""
Configuration pytest partagée pour tous les tests.
"""
import pytest
import sys
import os

# Assure que le projet est dans le PYTHONPATH
# (utile si pytest est lancé depuis un sous-dossier)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


def pytest_configure(config):
    """Enregistre les markers custom."""
    config.addinivalue_line(
        "markers",
        "integration: tests d'intégration (nécessitent HuggingFace embeddings + ChromaDB)"
    )
    config.addinivalue_line(
        "markers",
        "unit: tests unitaires rapides, aucune dépendance externe"
    )
    config.addinivalue_line(
        "markers",
        "ollama: tests nécessitant un serveur Ollama actif (localhost:11434)"
    )


@pytest.fixture(autouse=True)
def reset_memory_between_tests():
    """
    Réinitialise la mémoire de session avant chaque test
    pour éviter les effets de bord entre tests.
    """
    import importlib
    import app.memory.storage as mod
    importlib.reload(mod)
    yield
    mod.clear_memory()
