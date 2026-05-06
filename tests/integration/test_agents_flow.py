"""
Tests d'intégration : flux end-to-end des agents

Teste le graphe LangGraph complet (router → course_node / internship_node)
avec tous les appels LLM et externes mockés.
L'objectif est de valider que les données circulent correctement
d'un noeud à l'autre sans erreur.

Marqués @pytest.mark.integration — lancez avec :
    pytest -m integration
"""
import pytest
from unittest.mock import patch, MagicMock, mock_open


pytestmark = pytest.mark.integration

MOCK_PROFILE = "Ivan Elie, Master BIHAR, Python, ML, Deep Learning, MLOps."


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _mock_ollama_chain(return_value: str):
    """Retourne un mock qui simule prompt | llm | parser → return_value."""
    mock_chain = MagicMock()
    mock_chain.invoke.return_value = return_value
    mock_chain.__or__ = MagicMock(return_value=mock_chain)
    return mock_chain


# ---------------------------------------------------------------------------
# Test : flux cours complet (router → course_node)
# ---------------------------------------------------------------------------

class TestCourseAgentFlow:

    @patch("app.agents.course_agent.save_exchange")
    @patch("app.agents.course_agent.retrieve_context")
    @patch("app.agents.course_agent.ChatOllama")
    @patch("app.agents.course_agent.ChatPromptTemplate")
    @patch("app.agents.course_agent.StrOutputParser")
    def test_run_course_agent_returns_string(
        self, mock_parser, mock_prompt_cls, mock_llm, mock_retrieve, mock_save
    ):
        mock_retrieve.return_value = "[Extrait 1 - ml.pdf, p.1]\nLe gradient descent..."
        mock_chain = _mock_ollama_chain("Le gradient descent est un algorithme d'optimisation.")
        mock_prompt = MagicMock()
        mock_prompt.__or__ = MagicMock(return_value=mock_chain)
        mock_chain.__or__ = MagicMock(return_value=mock_chain)
        mock_prompt_cls.from_messages.return_value = mock_prompt

        from app.agents.course_agent import run_course_agent
        result = run_course_agent("Qu'est-ce que le gradient descent ?")

        assert isinstance(result, str)
        assert len(result) > 0

    @patch("app.agents.course_agent.save_exchange")
    @patch("app.agents.course_agent.retrieve_context")
    @patch("app.agents.course_agent.ChatOllama")
    @patch("app.agents.course_agent.ChatPromptTemplate")
    @patch("app.agents.course_agent.StrOutputParser")
    def test_run_course_agent_saves_to_memory(
        self, mock_parser, mock_prompt_cls, mock_llm, mock_retrieve, mock_save
    ):
        mock_retrieve.return_value = "Contexte"
        mock_chain = _mock_ollama_chain("Réponse IA")
        mock_prompt = MagicMock()
        mock_prompt.__or__ = MagicMock(return_value=mock_chain)
        mock_chain.__or__ = MagicMock(return_value=mock_chain)
        mock_prompt_cls.from_messages.return_value = mock_prompt

        from app.agents.course_agent import run_course_agent
        run_course_agent("Question test")

        mock_save.assert_called_once_with(
            human_msg="Question test",
            ai_msg="Réponse IA"
        )

    @patch("app.agents.course_agent.save_exchange")
    @patch("app.agents.course_agent.retrieve_context")
    @patch("app.agents.course_agent.ChatOllama")
    @patch("app.agents.course_agent.ChatPromptTemplate")
    @patch("app.agents.course_agent.StrOutputParser")
    def test_retrieve_context_called_with_question(
        self, mock_parser, mock_prompt_cls, mock_llm, mock_retrieve, mock_save
    ):
        mock_retrieve.return_value = "Contexte cours"
        mock_chain = _mock_ollama_chain("Réponse")
        mock_prompt = MagicMock()
        mock_prompt.__or__ = MagicMock(return_value=mock_chain)
        mock_chain.__or__ = MagicMock(return_value=mock_chain)
        mock_prompt_cls.from_messages.return_value = mock_prompt

        from app.agents.course_agent import run_course_agent
        run_course_agent("Explique le CNN")

        mock_retrieve.assert_called_once_with(query="Explique le CNN", k=4)

    @patch("app.agents.course_agent.save_exchange")
    @patch("app.agents.course_agent.retrieve_context")
    @patch("app.agents.course_agent.ChatOllama")
    @patch("app.agents.course_agent.ChatPromptTemplate")
    @patch("app.agents.course_agent.StrOutputParser")
    def test_generate_quiz_returns_questions(
        self, mock_parser, mock_prompt_cls, mock_llm, mock_retrieve, mock_save
    ):
        mock_retrieve.return_value = "Contexte ML"
        mock_chain = _mock_ollama_chain(
            "Q1. Qu'est-ce que le surapprentissage ?\nA) ...\nB) ...\nRéponse : A"
        )
        mock_prompt = MagicMock()
        mock_prompt.__or__ = MagicMock(return_value=mock_chain)
        mock_chain.__or__ = MagicMock(return_value=mock_chain)
        mock_prompt_cls.from_messages.return_value = mock_prompt

        from app.agents.course_agent import generate_quiz
        result = generate_quiz("overfitting", nb_questions=1)

        assert isinstance(result, str)
        assert len(result) > 0

    @patch("app.agents.course_agent.save_exchange")
    @patch("app.agents.course_agent.retrieve_context")
    @patch("app.agents.course_agent.ChatOllama")
    @patch("app.agents.course_agent.ChatPromptTemplate")
    @patch("app.agents.course_agent.StrOutputParser")
    def test_summarize_course_returns_structured_content(
        self, mock_parser, mock_prompt_cls, mock_llm, mock_retrieve, mock_save
    ):
        mock_retrieve.return_value = "Contexte Deep Learning"
        mock_chain = _mock_ollama_chain(
            "## Concept : Backpropagation\n### Définition\nAlgorithme de calcul de gradient."
        )
        mock_prompt = MagicMock()
        mock_prompt.__or__ = MagicMock(return_value=mock_chain)
        mock_chain.__or__ = MagicMock(return_value=mock_chain)
        mock_prompt_cls.from_messages.return_value = mock_prompt

        from app.agents.course_agent import summarize_course
        result = summarize_course("backpropagation")

        assert isinstance(result, str)


# ---------------------------------------------------------------------------
# Test : flux stage complet (router → internship_node)
# ---------------------------------------------------------------------------

class TestInternshipAgentFlow:

    @patch("app.agents.internship_agent.save_exchange")
    @patch("app.agents.internship_agent.score_job_offer")
    @patch("app.agents.internship_agent.search_internships")
    def test_full_internship_workflow(self, mock_search, mock_score, mock_save):
        mock_search.return_value = (
            "Airbus recherche un Data Scientist. "
            "Compétences : Python, MLOps, PyTorch. Stage 6 mois."
        )
        mock_score.return_value = {
            "score": 88,
            "points_forts": ["Python", "MLOps", "PyTorch"],
            "points_manquants": ["Scala"],
            "verdict": "Postuler"
        }

        from app.agents.internship_agent import run_internship_search
        result = run_internship_search("Data Scientist MLOps Toulouse")

        assert result["evaluation"]["score"] == 88
        assert result["evaluation"]["verdict"] == "Postuler"
        assert "report" in result
        assert "Postuler" in result["report"]

    @patch("app.agents.internship_agent.save_exchange")
    @patch("app.agents.internship_agent.score_job_offer")
    @patch("app.agents.internship_agent.search_internships")
    def test_low_score_generates_ignorer_verdict(self, mock_search, mock_score, mock_save):
        mock_search.return_value = "Offre nécessitant Java, Hadoop, Scala."
        mock_score.return_value = {
            "score": 40,
            "points_forts": ["Python"],
            "points_manquants": ["Java", "Hadoop", "Scala"],
            "verdict": "Ignorer"
        }

        from app.agents.internship_agent import run_internship_search
        result = run_internship_search("Backend Java Big Data")

        assert result["evaluation"]["verdict"] == "Ignorer"
        assert "Ignorer" in result["report"]


# ---------------------------------------------------------------------------
# Test : flux LangGraph end-to-end (router → bonne branche)
# ---------------------------------------------------------------------------

class TestLangGraphEndToEnd:

    def _patch_course_node(self, mock_response: str):
        return patch(
            "app.agents.router.run_course_agent",
            return_value=mock_response
        )

    def _patch_internship_node(self, mock_response: dict):
        return patch(
            "app.agents.router.run_internship_search",
            return_value=mock_response
        )

    def _patch_router_to(self, route: str):
        """Patche classify_intent pour forcer un route donné."""
        def fake_classify(state):
            return {**state, "route": route}
        return patch("app.agents.router.classify_intent", side_effect=fake_classify)

    def test_graph_routes_to_course_and_returns_response(self):
        with self._patch_router_to("cours"), \
             self._patch_course_node("Le CNN est un réseau convolutif."):

            from app.agents.router import run_agent
            result = run_agent("Qu'est-ce qu'un CNN ?")

            assert result == "Le CNN est un réseau convolutif."

    def test_graph_routes_to_internship_and_returns_report(self):
        fake_internship_result = {
            "query": "stage MLOps",
            "raw_results": "Offre Airbus",
            "evaluation": {"score": 90, "verdict": "Postuler"},
            "report": "## Rapport\nScore: 90/100 — Postuler"
        }

        with self._patch_router_to("stage"), \
             self._patch_internship_node(fake_internship_result):

            from app.agents.router import run_agent
            result = run_agent("Cherche un stage MLOps à Toulouse")

            assert "Rapport" in result or "90" in result

    def test_graph_state_response_is_string(self):
        with self._patch_router_to("cours"), \
             self._patch_course_node("Réponse de l'agent cours."):

            from app.agents.router import run_agent
            result = run_agent("Question quelconque")

            assert isinstance(result, str)


# ---------------------------------------------------------------------------
# Test : planner_agent
# ---------------------------------------------------------------------------

class TestPlannerAgentFlow:

    @patch("app.agents.planner_agent.ChatOllama")
    @patch("app.agents.planner_agent.ChatPromptTemplate")
    @patch("app.agents.planner_agent.StrOutputParser")
    def test_generate_study_plan_returns_string(
        self, mock_parser, mock_prompt_cls, mock_llm
    ):
        mock_chain = _mock_ollama_chain(
            "| Jour 1 | Machine Learning | 2h théorie | 1h exercices |"
        )
        mock_prompt = MagicMock()
        mock_prompt.__or__ = MagicMock(return_value=mock_chain)
        mock_chain.__or__ = MagicMock(return_value=mock_chain)
        mock_prompt_cls.from_messages.return_value = mock_prompt

        from app.agents.planner_agent import generate_study_plan
        result = generate_study_plan(
            topics=["Machine Learning", "Deep Learning"],
            exam_date="2026-05-15",
            hours_per_day=3
        )

        assert isinstance(result, str)
        assert len(result) > 0

    @patch("app.agents.planner_agent.ChatOllama")
    @patch("app.agents.planner_agent.ChatPromptTemplate")
    @patch("app.agents.planner_agent.StrOutputParser")
    def test_prioritize_tasks_returns_string(
        self, mock_parser, mock_prompt_cls, mock_llm
    ):
        mock_chain = _mock_ollama_chain(
            "Urgent + Important:\n- Réviser ML\nImportant:\n- Lire article NLP"
        )
        mock_prompt = MagicMock()
        mock_prompt.__or__ = MagicMock(return_value=mock_chain)
        mock_chain.__or__ = MagicMock(return_value=mock_chain)
        mock_prompt_cls.from_messages.return_value = mock_prompt

        from app.agents.planner_agent import prioritize_tasks
        result = prioritize_tasks(["Réviser ML", "Lire article NLP", "Faire exercice CNN"])

        assert isinstance(result, str)

    @patch("app.agents.planner_agent.ChatOllama")
    @patch("app.agents.planner_agent.ChatPromptTemplate")
    @patch("app.agents.planner_agent.StrOutputParser")
    def test_study_plan_includes_exam_date(
        self, mock_parser, mock_prompt_cls, mock_llm
    ):
        """Vérifie que la date d'examen est passée au prompt."""
        captured_invoke_args = {}

        def fake_invoke(args):
            captured_invoke_args.update(args)
            return "Plan généré"

        mock_chain = MagicMock()
        mock_chain.invoke.side_effect = fake_invoke
        mock_chain.__or__ = MagicMock(return_value=mock_chain)
        mock_prompt = MagicMock()
        mock_prompt.__or__ = MagicMock(return_value=mock_chain)
        mock_prompt_cls.from_messages.return_value = mock_prompt

        from app.agents.planner_agent import generate_study_plan
        generate_study_plan(
            topics=["CNN"],
            exam_date="2026-06-01",
            hours_per_day=2
        )

        assert captured_invoke_args.get("exam_date") == "2026-06-01"
        assert captured_invoke_args.get("hours_per_day") == 2
