"""
Tests HTTP des endpoints de l'API AI Personal Agent.

Utilisé dans deux contextes :
  - En local avec TestClient (FastAPI) : tous les appels LLM sont mockés
  - En CI (GitHub Actions) : contre un vrai conteneur Docker sur localhost:8000

La variable d'environnement API_BASE_URL contrôle le mode :
  - Non définie (ou "local") → TestClient FastAPI (pas de réseau)
  - Définie (ex: "http://localhost:8000") → requêtes HTTP réelles (httpx)
"""
import os
import pytest
from unittest.mock import patch, MagicMock


# ---------------------------------------------------------------------------
# Fixture : client HTTP selon le contexte d'exécution
# ---------------------------------------------------------------------------

API_BASE_URL = os.getenv("API_BASE_URL", "local")


def _mock_ollama_chain(return_value):
    """Retourne un mock de chaîne LangChain → return_value."""
    chain = MagicMock()
    chain.invoke.return_value = return_value
    chain.__or__ = MagicMock(return_value=chain)
    return chain


@pytest.fixture(scope="module")
def client():
    if API_BASE_URL == "local":
        # Mode local : TestClient FastAPI avec LLM mockés
        from fastapi.testclient import TestClient
        from api.main import app
        with TestClient(app) as c:
            yield c
    else:
        # Mode CI : requêtes réelles contre le conteneur Docker
        import httpx
        with httpx.Client(base_url=API_BASE_URL, timeout=30) as c:
            yield c


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _mock_prompt():
    """Mock de ChatPromptTemplate."""
    mock = MagicMock()
    mock.__or__ = MagicMock(return_value=MagicMock())
    return mock


def post(client, url, json):
    """Appel POST compatible TestClient et httpx."""
    return client.post(url, json=json)


def get(client, url):
    """Appel GET compatible TestClient et httpx."""
    return client.get(url)


# ===========================================================================
# GET /health
# ===========================================================================

class TestHealth:

    def test_status_ok(self, client):
        r = get(client, "/health")
        assert r.status_code == 200

    def test_response_has_status_field(self, client):
        r = get(client, "/health")
        assert r.json()["status"] == "ok"

    def test_response_has_model_field(self, client):
        r = get(client, "/health")
        assert "model" in r.json()

    def test_response_has_version_field(self, client):
        r = get(client, "/health")
        assert "version" in r.json()


# ===========================================================================
# POST /courses/ask
# ===========================================================================

class TestCoursesAsk:

    @pytest.fixture(autouse=True)
    def _mock_llm(self):
        chain = _mock_ollama_chain("Le gradient descent minimise la fonction de coût.")
        with patch("app.agents.course_agent.retrieve_context", return_value="[Extrait 1]\nContenu cours"), \
             patch("app.agents.course_agent.save_exchange"), \
             patch("app.agents.course_agent.ChatOllama"), \
             patch("app.agents.course_agent.ChatPromptTemplate") as mp, \
             patch("app.agents.course_agent.StrOutputParser"):
            mp.from_messages.return_value.__or__ = MagicMock(return_value=chain)
            chain.__or__ = MagicMock(return_value=chain)
            yield

    def test_returns_200(self, client):
        r = post(client, "/courses/ask", {"question": "Qu'est-ce que le gradient descent ?"})
        assert r.status_code == 200

    def test_response_has_answer_field(self, client):
        r = post(client, "/courses/ask", {"question": "Explique le CNN"})
        assert "answer" in r.json()

    def test_answer_is_non_empty_string(self, client):
        r = post(client, "/courses/ask", {"question": "Qu'est-ce que la régularisation ?"})
        assert isinstance(r.json()["answer"], str)
        assert len(r.json()["answer"]) > 0

    def test_empty_question_returns_422(self, client):
        r = post(client, "/courses/ask", {"question": ""})
        assert r.status_code == 422

    def test_missing_question_returns_422(self, client):
        r = post(client, "/courses/ask", {})
        assert r.status_code == 422


# ===========================================================================
# POST /courses/quiz
# ===========================================================================

class TestCoursesQuiz:

    @pytest.fixture(autouse=True)
    def _mock_llm(self):
        chain = _mock_ollama_chain("Q1. Qu'est-ce que le surapprentissage ?\nA) ...\nRéponse : A")
        with patch("app.agents.course_agent.retrieve_context", return_value="Contexte cours"), \
             patch("app.agents.course_agent.save_exchange"), \
             patch("app.agents.course_agent.ChatOllama"), \
             patch("app.agents.course_agent.ChatPromptTemplate") as mp, \
             patch("app.agents.course_agent.StrOutputParser"):
            mp.from_messages.return_value.__or__ = MagicMock(return_value=chain)
            chain.__or__ = MagicMock(return_value=chain)
            yield

    def test_returns_200(self, client):
        r = post(client, "/courses/quiz", {"topic": "overfitting", "nb_questions": 2})
        assert r.status_code == 200

    def test_response_has_quiz_field(self, client):
        r = post(client, "/courses/quiz", {"topic": "CNN", "nb_questions": 3})
        assert "quiz" in r.json()

    def test_response_echoes_topic(self, client):
        r = post(client, "/courses/quiz", {"topic": "backpropagation", "nb_questions": 1})
        assert r.json()["topic"] == "backpropagation"

    def test_response_echoes_nb_questions(self, client):
        r = post(client, "/courses/quiz", {"topic": "CNN", "nb_questions": 2})
        assert r.json()["nb_questions"] == 2

    def test_nb_questions_above_10_returns_422(self, client):
        r = post(client, "/courses/quiz", {"topic": "ML", "nb_questions": 15})
        assert r.status_code == 422

    def test_default_nb_questions_is_3(self, client):
        r = post(client, "/courses/quiz", {"topic": "RNN"})
        assert r.json()["nb_questions"] == 3


# ===========================================================================
# POST /courses/summary
# ===========================================================================

class TestCoursesSummary:

    @pytest.fixture(autouse=True)
    def _mock_llm(self):
        chain = _mock_ollama_chain("## Concept : CNN\n### Définition\nRéseau convolutif.")
        with patch("app.agents.course_agent.retrieve_context", return_value="Contexte"), \
             patch("app.agents.course_agent.save_exchange"), \
             patch("app.agents.course_agent.ChatOllama"), \
             patch("app.agents.course_agent.ChatPromptTemplate") as mp, \
             patch("app.agents.course_agent.StrOutputParser"):
            mp.from_messages.return_value.__or__ = MagicMock(return_value=chain)
            chain.__or__ = MagicMock(return_value=chain)
            yield

    def test_returns_200(self, client):
        r = post(client, "/courses/summary", {"topic": "CNN"})
        assert r.status_code == 200

    def test_response_has_summary_field(self, client):
        r = post(client, "/courses/summary", {"topic": "LSTM"})
        assert "summary" in r.json()

    def test_response_echoes_topic(self, client):
        r = post(client, "/courses/summary", {"topic": "dropout"})
        assert r.json()["topic"] == "dropout"


# ===========================================================================
# POST /internship/search
# ===========================================================================

class TestInternshipSearch:

    @pytest.fixture(autouse=True)
    def _mock_llm(self):
        with patch("app.agents.internship_agent.search_internships",
                   return_value="Offre Airbus Data Scientist MLOps Python PyTorch"), \
             patch("app.agents.internship_agent.score_job_offer", return_value={
                 "score": 88,
                 "points_forts": ["Python", "MLOps"],
                 "points_manquants": ["Scala"],
                 "verdict": "Postuler",
             }), \
             patch("app.agents.internship_agent.save_exchange"):
            yield

    def test_returns_200(self, client):
        r = post(client, "/internship/search", {"query": "Data Scientist Paris"})
        assert r.status_code == 200

    def test_response_has_score(self, client):
        r = post(client, "/internship/search", {"query": "MLOps Toulouse"})
        assert r.json()["score"] == 88

    def test_response_has_verdict(self, client):
        r = post(client, "/internship/search", {"query": "NLP Engineer"})
        assert r.json()["verdict"] in ("Postuler", "Ignorer")

    def test_response_has_points_forts(self, client):
        r = post(client, "/internship/search", {"query": "Data Scientist"})
        assert isinstance(r.json()["points_forts"], list)

    def test_response_has_points_manquants(self, client):
        r = post(client, "/internship/search", {"query": "Data Scientist"})
        assert isinstance(r.json()["points_manquants"], list)

    def test_response_has_report(self, client):
        r = post(client, "/internship/search", {"query": "Data Scientist"})
        assert "report" in r.json()
        assert len(r.json()["report"]) > 0

    def test_empty_query_returns_422(self, client):
        r = post(client, "/internship/search", {"query": ""})
        assert r.status_code == 422

    def test_no_results_returns_404(self, client):
        with patch("app.agents.internship_agent.search_internships", return_value=""):
            r = post(client, "/internship/search", {"query": "stage introuvable"})
            assert r.status_code == 404


# ===========================================================================
# POST /internship/cover-letter
# ===========================================================================

class TestInternshipCoverLetter:

    @pytest.fixture(autouse=True)
    def _mock_llm(self):
        chain = _mock_ollama_chain("Madame, Monsieur, Je me permets de vous adresser...")
        with patch("app.agents.internship_agent.save_exchange"), \
             patch("app.agents.internship_agent.ChatOllama"), \
             patch("app.agents.internship_agent.ChatPromptTemplate") as mp, \
             patch("app.agents.internship_agent.StrOutputParser"), \
             patch("builtins.open", return_value=MagicMock(
                 __enter__=MagicMock(return_value=MagicMock(read=MagicMock(return_value="Profil Ivan"))),
                 __exit__=MagicMock(return_value=False)
             )):
            mp.from_messages.return_value.__or__ = MagicMock(return_value=chain)
            chain.__or__ = MagicMock(return_value=chain)
            yield

    def test_returns_200(self, client):
        r = post(client, "/internship/cover-letter",
                 {"job_description": "Stage Data Scientist 6 mois, Python requis."})
        assert r.status_code == 200

    def test_response_has_letter_field(self, client):
        r = post(client, "/internship/cover-letter",
                 {"job_description": "Poste MLOps Engineer, Airbus Toulouse."})
        assert "letter" in r.json()

    def test_short_description_returns_422(self, client):
        r = post(client, "/internship/cover-letter", {"job_description": "court"})
        assert r.status_code == 422


# ===========================================================================
# POST /internship/hr-email
# ===========================================================================

class TestInternshipHrEmail:

    @pytest.fixture(autouse=True)
    def _mock_llm(self):
        chain = _mock_ollama_chain("Objet: Candidature Data Scientist\nCorps: Bonjour...")
        with patch("app.agents.internship_agent.ChatOllama"), \
             patch("app.agents.internship_agent.ChatPromptTemplate") as mp, \
             patch("app.agents.internship_agent.StrOutputParser"), \
             patch("builtins.open", return_value=MagicMock(
                 __enter__=MagicMock(return_value=MagicMock(read=MagicMock(return_value="Profil"))),
                 __exit__=MagicMock(return_value=False)
             )):
            mp.from_messages.return_value.__or__ = MagicMock(return_value=chain)
            chain.__or__ = MagicMock(return_value=chain)
            yield

    def test_returns_200(self, client):
        r = post(client, "/internship/hr-email",
                 {"company": "Airbus", "job_title": "Data Scientist"})
        assert r.status_code == 200

    def test_response_has_email_field(self, client):
        r = post(client, "/internship/hr-email",
                 {"company": "SNCF", "job_title": "MLOps Engineer"})
        assert "email" in r.json()

    def test_missing_company_returns_422(self, client):
        r = post(client, "/internship/hr-email", {"job_title": "Data Scientist"})
        assert r.status_code == 422

    def test_missing_job_title_returns_422(self, client):
        r = post(client, "/internship/hr-email", {"company": "Airbus"})
        assert r.status_code == 422


# ===========================================================================
# POST /planner/study-plan
# ===========================================================================

class TestPlannerStudyPlan:

    @pytest.fixture(autouse=True)
    def _mock_llm(self):
        chain = _mock_ollama_chain("| Jour 1 | Machine Learning | 2h |")
        with patch("app.agents.planner_agent.ChatOllama"), \
             patch("app.agents.planner_agent.ChatPromptTemplate") as mp, \
             patch("app.agents.planner_agent.StrOutputParser"):
            mp.from_messages.return_value.__or__ = MagicMock(return_value=chain)
            chain.__or__ = MagicMock(return_value=chain)
            yield

    def test_returns_200(self, client):
        r = post(client, "/planner/study-plan", {
            "topics": ["Machine Learning", "Deep Learning"],
            "exam_date": "2026-06-01",
            "hours_per_day": 3,
        })
        assert r.status_code == 200

    def test_response_has_plan_field(self, client):
        r = post(client, "/planner/study-plan", {
            "topics": ["CNN"],
            "exam_date": "2026-05-20",
            "hours_per_day": 2,
        })
        assert "plan" in r.json()

    def test_response_echoes_exam_date(self, client):
        r = post(client, "/planner/study-plan", {
            "topics": ["NLP"],
            "exam_date": "2026-06-15",
            "hours_per_day": 2,
        })
        assert r.json()["exam_date"] == "2026-06-15"

    def test_response_echoes_topics(self, client):
        topics = ["ML", "DL", "MLOps"]
        r = post(client, "/planner/study-plan", {
            "topics": topics,
            "exam_date": "2026-06-01",
            "hours_per_day": 2,
        })
        assert r.json()["topics"] == topics

    def test_empty_topics_returns_422(self, client):
        r = post(client, "/planner/study-plan", {
            "topics": [],
            "exam_date": "2026-06-01",
        })
        assert r.status_code == 422

    def test_hours_above_12_returns_422(self, client):
        r = post(client, "/planner/study-plan", {
            "topics": ["ML"],
            "exam_date": "2026-06-01",
            "hours_per_day": 15,
        })
        assert r.status_code == 422


# ===========================================================================
# POST /planner/prioritize
# ===========================================================================

class TestPlannerPrioritize:

    @pytest.fixture(autouse=True)
    def _mock_llm(self):
        chain = _mock_ollama_chain("Urgent + Important:\n- Réviser ML\nImportant:\n- Lire NLP")
        with patch("app.agents.planner_agent.ChatOllama"), \
             patch("app.agents.planner_agent.ChatPromptTemplate") as mp, \
             patch("app.agents.planner_agent.StrOutputParser"):
            mp.from_messages.return_value.__or__ = MagicMock(return_value=chain)
            chain.__or__ = MagicMock(return_value=chain)
            yield

    def test_returns_200(self, client):
        r = post(client, "/planner/prioritize",
                 {"tasks": ["Réviser ML", "Lire NLP", "TP CNN"]})
        assert r.status_code == 200

    def test_response_has_prioritized_field(self, client):
        r = post(client, "/planner/prioritize",
                 {"tasks": ["Tâche A", "Tâche B"]})
        assert "prioritized" in r.json()

    def test_empty_tasks_returns_422(self, client):
        r = post(client, "/planner/prioritize", {"tasks": []})
        assert r.status_code == 422


# ===========================================================================
# GET /memory/history
# ===========================================================================

class TestMemoryHistory:

    def test_returns_200(self, client):
        r = get(client, "/memory/history")
        assert r.status_code == 200

    def test_response_has_history_field(self, client):
        r = get(client, "/memory/history")
        assert "history" in r.json()

    def test_history_is_list(self, client):
        r = get(client, "/memory/history")
        assert isinstance(r.json()["history"], list)

    def test_response_has_count_field(self, client):
        r = get(client, "/memory/history")
        assert "count" in r.json()

    def test_count_matches_history_length(self, client):
        r = get(client, "/memory/history")
        data = r.json()
        assert data["count"] == len(data["history"])


# ===========================================================================
# POST /memory/clear
# ===========================================================================

class TestMemoryClear:

    def test_returns_200(self, client):
        r = post(client, "/memory/clear", {})
        assert r.status_code == 200

    def test_response_status_ok(self, client):
        r = post(client, "/memory/clear", {})
        assert r.json()["status"] == "ok"

    def test_history_empty_after_clear(self, client):
        post(client, "/memory/clear", {})
        r = get(client, "/memory/history")
        assert r.json()["count"] == 0
