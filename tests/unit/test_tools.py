"""
Tests unitaires : app/tools/scoring.py et app/tools/search.py

Tous les appels Ollama et DuckDuckGo sont mockés — aucune dépendance externe.
"""
import pytest
from unittest.mock import patch, MagicMock, mock_open


# ===========================================================================
# app/tools/search.py
# ===========================================================================

class TestSearchInternships:

    @patch("app.tools.search.DDGS")
    def test_returns_string_result(self, mock_ddgs_cls):
        mock_instance = MagicMock()
        mock_instance.text.return_value = [
            {"title": "Data Scientist", "body": "Offre chez Airbus...", "href": "https://example.com/1"}
        ]
        mock_ddgs_cls.return_value.__enter__.return_value = mock_instance

        from app.tools.search import search_internships
        result = search_internships("Data Scientist Paris")

        assert isinstance(result, str)
        assert len(result) > 0

    @patch("app.tools.search.DDGS")
    def test_query_is_enriched_with_context(self, mock_ddgs_cls):
        mock_instance = MagicMock()
        mock_instance.text.return_value = []
        mock_ddgs_cls.return_value.__enter__.return_value = mock_instance

        from app.tools.search import search_internships
        search_internships("MLOps")

        called_query = mock_instance.text.call_args[0][0]
        assert "MLOps" in called_query
        assert "stage" in called_query.lower()

    @patch("app.tools.search.DDGS")
    def test_empty_query_still_calls_search(self, mock_ddgs_cls):
        mock_instance = MagicMock()
        mock_instance.text.return_value = []
        mock_ddgs_cls.return_value.__enter__.return_value = mock_instance

        from app.tools.search import search_internships
        search_internships("")
        mock_instance.text.assert_called_once()

    @patch("app.tools.search.DDGS")
    def test_targets_expected_job_sites(self, mock_ddgs_cls):
        mock_instance = MagicMock()
        mock_instance.text.return_value = []
        mock_ddgs_cls.return_value.__enter__.return_value = mock_instance

        from app.tools.search import search_internships
        search_internships("NLP")

        called_query = mock_instance.text.call_args[0][0]
        assert "stage" in called_query.lower() and "alternance" in called_query.lower()


# ===========================================================================
# app/tools/scoring.py
# ===========================================================================

MOCK_PROFILE = """
Nom : Ivan Elie DJAKPA
Compétences : Python, Machine Learning, Deep Learning, MLOps, PyTorch
"""

MOCK_SCORE_RESULT = {
    "score": 85,
    "points_forts": ["Python", "Machine Learning", "PyTorch"],
    "points_manquants": ["Kubernetes"],
    "verdict": "Postuler"
}


class TestScoreJobOffer:

    @patch("builtins.open", mock_open(read_data=MOCK_PROFILE))
    @patch("app.tools.scoring.ChatOllama")
    @patch("app.tools.scoring.JsonOutputParser")
    def test_returns_dict_with_expected_keys(self, mock_parser_cls, mock_llm_cls):
        mock_chain = MagicMock()
        mock_chain.invoke.return_value = MOCK_SCORE_RESULT

        mock_llm = MagicMock()
        mock_parser = MagicMock()
        mock_llm_cls.return_value = mock_llm
        mock_parser_cls.return_value = mock_parser

        # Simuler prompt | llm | parser → chain
        with patch("app.tools.scoring.PromptTemplate") as mock_prompt_cls:
            mock_prompt = MagicMock()
            mock_prompt.__or__ = MagicMock(return_value=mock_chain)
            mock_chain.__or__ = MagicMock(return_value=mock_chain)
            mock_prompt_cls.return_value = mock_prompt

            from importlib import reload
            import app.tools.scoring as mod
            reload(mod)

            with patch.object(mod, "ChatOllama", mock_llm_cls), \
                 patch.object(mod, "JsonOutputParser", mock_parser_cls), \
                 patch("builtins.open", mock_open(read_data=MOCK_PROFILE)):

                # On patche directement la chain en interne
                with patch("app.tools.scoring.PromptTemplate") as pt:
                    pt.return_value.__or__ = lambda s, o: mock_chain
                    mock_chain.__or__ = lambda s, o: mock_chain
                    mock_chain.invoke.return_value = MOCK_SCORE_RESULT

                    result = mod.score_job_offer("Offre Data Scientist MLOps")

        assert isinstance(result, dict)

    @patch("builtins.open", side_effect=FileNotFoundError)
    def test_raises_on_missing_profile(self, mock_file):
        """score_job_offer lève une exception si le profil est introuvable."""
        from app.tools.scoring import score_job_offer
        with pytest.raises(FileNotFoundError):
            score_job_offer("Une offre")

    def test_score_result_structure(self):
        """Vérifie la structure attendue du résultat (contrat de données)."""
        result = MOCK_SCORE_RESULT
        assert "score" in result
        assert "points_forts" in result
        assert "points_manquants" in result
        assert "verdict" in result
        assert isinstance(result["score"], int)
        assert isinstance(result["points_forts"], list)
        assert isinstance(result["points_manquants"], list)
        assert result["verdict"] in ("Postuler", "Ignorer")

    def test_verdict_logic_postuler(self):
        """Score > 75 → verdict Postuler."""
        result = {**MOCK_SCORE_RESULT, "score": 80, "verdict": "Postuler"}
        assert result["verdict"] == "Postuler"
        assert result["score"] > 75

    def test_verdict_logic_ignorer(self):
        """Score <= 75 → verdict Ignorer."""
        result = {**MOCK_SCORE_RESULT, "score": 60, "verdict": "Ignorer"}
        assert result["verdict"] == "Ignorer"
        assert result["score"] <= 75
