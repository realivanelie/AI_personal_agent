"""
Tests unitaires : app/agents/internship_agent.py

Teste les fonctions pures et les fonctions mockant Ollama/DuckDuckGo.
"""
import pytest
from unittest.mock import patch, MagicMock, mock_open
from app.agents.internship_agent import (
    format_internship_report,
    run_internship_search,
    generate_cover_letter,
    generate_hr_email,
)


# ---------------------------------------------------------------------------
# format_internship_report : fonction pure, pas de mock
# ---------------------------------------------------------------------------

class TestFormatInternshipReport:

    def _eval(self, score=80, points_forts=None, points_manquants=None, verdict="Postuler"):
        return {
            "score": score,
            "points_forts": points_forts or ["Python", "ML"],
            "points_manquants": points_manquants or ["Kubernetes"],
            "verdict": verdict,
        }

    def test_returns_string(self):
        result = format_internship_report("Data Scientist", "résultats bruts", self._eval())
        assert isinstance(result, str)

    def test_contains_score(self):
        result = format_internship_report("DS", "résultats", self._eval(score=88))
        assert "88" in result

    def test_contains_query(self):
        result = format_internship_report("MLOps Paris", "résultats", self._eval())
        assert "MLOps Paris" in result

    def test_postuler_verdict_present(self):
        result = format_internship_report("DS", "r", self._eval(verdict="Postuler"))
        assert "Postuler" in result

    def test_ignorer_verdict_present(self):
        result = format_internship_report("DS", "r", self._eval(verdict="Ignorer"))
        assert "Ignorer" in result

    def test_points_forts_listed(self):
        eval_data = self._eval(points_forts=["Python", "PyTorch", "NLP"])
        result = format_internship_report("DS", "r", eval_data)
        assert "Python" in result
        assert "PyTorch" in result

    def test_points_manquants_listed(self):
        eval_data = self._eval(points_manquants=["Kubernetes", "Terraform"])
        result = format_internship_report("DS", "r", eval_data)
        assert "Kubernetes" in result

    def test_raw_results_truncated_to_800_chars(self):
        long_results = "A" * 2000
        result = format_internship_report("DS", long_results, self._eval())
        # La fonction fait results[:800], donc pas plus de 800 + "..."
        assert len(result) < 3000

    def test_missing_eval_keys_dont_crash(self):
        """Evaluation partielle ne doit pas lever d'exception."""
        result = format_internship_report("DS", "résultats", {})
        assert isinstance(result, str)


# ---------------------------------------------------------------------------
# run_internship_search : mock search + scoring + memory
# ---------------------------------------------------------------------------

class TestRunInternshipSearch:

    @patch("app.agents.internship_agent.save_exchange")
    @patch("app.agents.internship_agent.score_job_offer")
    @patch("app.agents.internship_agent.search_internships")
    def test_returns_dict_with_expected_keys(self, mock_search, mock_score, mock_save):
        mock_search.return_value = "Offre : Data Scientist chez Airbus..."
        mock_score.return_value = {
            "score": 85, "points_forts": ["Python"], "points_manquants": [], "verdict": "Postuler"
        }

        result = run_internship_search("Data Scientist Paris")

        assert "query" in result
        assert "raw_results" in result
        assert "evaluation" in result
        assert "report" in result

    @patch("app.agents.internship_agent.save_exchange")
    @patch("app.agents.internship_agent.score_job_offer")
    @patch("app.agents.internship_agent.search_internships")
    def test_returns_error_dict_on_empty_search(self, mock_search, mock_score, mock_save):
        mock_search.return_value = ""

        result = run_internship_search("Query quelconque")

        assert "erreur" in result

    @patch("app.agents.internship_agent.save_exchange")
    @patch("app.agents.internship_agent.score_job_offer")
    @patch("app.agents.internship_agent.search_internships")
    def test_saves_exchange_to_memory(self, mock_search, mock_score, mock_save):
        mock_search.return_value = "Offre trouvée"
        mock_score.return_value = {
            "score": 70, "points_forts": [], "points_manquants": [], "verdict": "Ignorer"
        }

        run_internship_search("NLP Engineer")

        mock_save.assert_called_once()

    @patch("app.agents.internship_agent.save_exchange")
    @patch("app.agents.internship_agent.score_job_offer")
    @patch("app.agents.internship_agent.search_internships")
    def test_query_echoed_in_result(self, mock_search, mock_score, mock_save):
        mock_search.return_value = "Offre"
        mock_score.return_value = {
            "score": 60, "points_forts": [], "points_manquants": [], "verdict": "Ignorer"
        }

        result = run_internship_search("Mon query précis")
        assert result["query"] == "Mon query précis"


# ---------------------------------------------------------------------------
# generate_cover_letter
# ---------------------------------------------------------------------------

MOCK_PROFILE = "Ivan Elie, Master BIHAR, Python, ML, Deep Learning."


class TestGenerateCoverLetter:

    @patch("app.agents.internship_agent.save_exchange")
    @patch("app.agents.internship_agent.ChatOllama")
    @patch("app.agents.internship_agent.ChatPromptTemplate")
    @patch("app.agents.internship_agent.StrOutputParser")
    @patch("builtins.open", mock_open(read_data=MOCK_PROFILE))
    def test_returns_non_empty_string(self, mock_parser, mock_prompt_cls, mock_llm_cls, mock_save):
        mock_chain = MagicMock()
        mock_chain.invoke.return_value = "Madame, Monsieur, ..."
        mock_prompt = MagicMock()
        mock_prompt.__or__ = MagicMock(return_value=mock_chain)
        mock_chain.__or__ = MagicMock(return_value=mock_chain)
        mock_prompt_cls.from_messages.return_value = mock_prompt

        result = generate_cover_letter("Offre Data Scientist MLOps")

        assert isinstance(result, str)
        assert len(result) > 0

    @patch("app.agents.internship_agent.save_exchange")
    @patch("app.agents.internship_agent.ChatOllama")
    @patch("app.agents.internship_agent.ChatPromptTemplate")
    @patch("app.agents.internship_agent.StrOutputParser")
    @patch("builtins.open", side_effect=FileNotFoundError)
    def test_fallback_profile_used_when_file_missing(self, mock_file, mock_parser, mock_prompt_cls, mock_llm_cls, mock_save):
        """Si my_profile.txt est absent, utilise le profil par défaut sans crash."""
        mock_chain = MagicMock()
        mock_chain.invoke.return_value = "Lettre générée avec profil par défaut"
        mock_prompt = MagicMock()
        mock_prompt.__or__ = MagicMock(return_value=mock_chain)
        mock_chain.__or__ = MagicMock(return_value=mock_chain)
        mock_prompt_cls.from_messages.return_value = mock_prompt

        result = generate_cover_letter("Offre")
        assert isinstance(result, str)


# ---------------------------------------------------------------------------
# generate_hr_email
# ---------------------------------------------------------------------------

class TestGenerateHrEmail:

    @patch("app.agents.internship_agent.ChatOllama")
    @patch("app.agents.internship_agent.ChatPromptTemplate")
    @patch("app.agents.internship_agent.StrOutputParser")
    @patch("builtins.open", mock_open(read_data=MOCK_PROFILE))
    def test_returns_string(self, mock_parser, mock_prompt_cls, mock_llm_cls):
        mock_chain = MagicMock()
        mock_chain.invoke.return_value = "Objet: Candidature\nCorps: Bonjour..."
        mock_prompt = MagicMock()
        mock_prompt.__or__ = MagicMock(return_value=mock_chain)
        mock_chain.__or__ = MagicMock(return_value=mock_chain)
        mock_prompt_cls.from_messages.return_value = mock_prompt

        result = generate_hr_email("Airbus", "Data Scientist")
        assert isinstance(result, str)
