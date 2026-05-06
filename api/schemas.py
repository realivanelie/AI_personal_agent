"""
Modèles Pydantic — contrats de données de l'API AI Personal Agent.
"""
from pydantic import BaseModel, Field
from typing import Optional


# Requêtes

class QuestionRequest(BaseModel):
    question: str = Field(..., min_length=1, description="Question à poser à l'agent")

    model_config = {"json_schema_extra": {"example": {"question": "Explique le gradient descent"}}}


class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, description="Requête de recherche de stage")

    model_config = {"json_schema_extra": {"example": {"query": "Data Scientist MLOps Paris"}}}


class QuizRequest(BaseModel):
    topic: str = Field(..., min_length=1, description="Thème du quiz")
    nb_questions: int = Field(default=3, ge=1, le=10, description="Nombre de questions (1-10)")

    model_config = {"json_schema_extra": {"example": {"topic": "réseaux de neurones", "nb_questions": 3}}}


class SummaryRequest(BaseModel):
    topic: str = Field(..., min_length=1, description="Concept à résumer")

    model_config = {"json_schema_extra": {"example": {"topic": "régularisation L2"}}}


class CoverLetterRequest(BaseModel):
    job_description: str = Field(..., min_length=10, description="Description du poste")

    model_config = {"json_schema_extra": {"example": {"job_description": "Stage Data Scientist 6 mois, Python, MLOps requis."}}}


class HrEmailRequest(BaseModel):
    company: str = Field(..., min_length=1, description="Nom de l'entreprise")
    job_title: str = Field(..., min_length=1, description="Intitulé du poste")

    model_config = {"json_schema_extra": {"example": {"company": "Airbus", "job_title": "Data Scientist"}}}


class StudyPlanRequest(BaseModel):
    topics: list[str] = Field(..., min_length=1, description="Liste des thèmes à réviser")
    exam_date: str = Field(..., description="Date de l'examen (YYYY-MM-DD)")
    hours_per_day: int = Field(default=2, ge=1, le=12, description="Heures de travail par jour")

    model_config = {
        "json_schema_extra": {
            "example": {
                "topics": ["Machine Learning", "Deep Learning"],
                "exam_date": "2026-06-01",
                "hours_per_day": 3,
            }
        }
    }


class PrioritizeRequest(BaseModel):
    tasks: list[str] = Field(..., min_length=1, description="Liste des tâches à prioriser")

    model_config = {
        "json_schema_extra": {
            "example": {"tasks": ["Réviser CNN", "Faire TP MLOps", "Lire article NLP"]}
        }
    }


# Réponses

class HealthResponse(BaseModel):
    status: str
    model: str
    version: str


class AgentResponse(BaseModel):
    response: str
    route: Optional[str] = None


class CourseResponse(BaseModel):
    answer: str


class QuizResponse(BaseModel):
    quiz: str
    topic: str
    nb_questions: int


class SummaryResponse(BaseModel):
    summary: str
    topic: str


class InternshipResponse(BaseModel):
    query: str
    score: Optional[int] = None
    verdict: Optional[str] = None
    points_forts: list[str] = []
    points_manquants: list[str] = []
    report: str
    raw_results: Optional[str] = None


class CoverLetterResponse(BaseModel):
    letter: str


class HrEmailResponse(BaseModel):
    email: str


class StudyPlanResponse(BaseModel):
    plan: str
    exam_date: str
    topics: list[str]


class PrioritizeResponse(BaseModel):
    prioritized: str


class HistoryResponse(BaseModel):
    history: list[dict]
    count: int


class ErrorResponse(BaseModel):
    detail: str
