"""
API FastAPI — AI Personal Agent

Endpoints :
  GET  /health                  → statut du service
  POST /agent/ask               → router LangGraph (cours ou stage auto-détecté)
  POST /courses/ask             → question RAG sur les cours
  POST /courses/quiz            → génération de QCM
  POST /courses/summary         → résumé structuré d'un concept
  POST /internship/search       → recherche + scoring d'offres de stage
  POST /internship/cover-letter → génération de lettre de motivation
  POST /internship/hr-email     → génération d'email RH
  POST /planner/study-plan      → plan de révision jour par jour
  POST /planner/prioritize      → priorisation de tâches (Eisenhower)
  GET  /memory/history          → historique de la session
  POST /memory/clear            → réinitialisation de la mémoire
"""
import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse

from api.schemas import (
    QuestionRequest, SearchRequest, QuizRequest, SummaryRequest,
    CoverLetterRequest, HrEmailRequest, StudyPlanRequest, PrioritizeRequest,
    HealthResponse, AgentResponse, CourseResponse, QuizResponse, SummaryResponse,
    InternshipResponse, CoverLetterResponse, HrEmailResponse,
    StudyPlanResponse, PrioritizeResponse, HistoryResponse,
)
from app.config import Config

app = FastAPI(
    title="AI Personal Agent API",
    description="API REST pour l'agent IA académique — cours, stage, planification.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)


# Health

@app.get("/health", response_model=HealthResponse, tags=["Monitoring"])
def health():
    """Vérifie que le service est opérationnel."""
    return HealthResponse(
        status="ok",
        model=Config.LLM_MODEL,
        version=os.getenv("COMMIT_ID", "dev"),
    )


# Agent — routage automatique

@app.post("/agent/ask", response_model=AgentResponse, tags=["Agent"])
def agent_ask(body: QuestionRequest):
    """
    Envoie une question au routeur LangGraph.
    L'intention (cours / stage) est détectée automatiquement.
    """
    try:
        from app.agents.router import run_agent, build_agent_graph, AgentState

        agent = build_agent_graph()
        initial_state: AgentState = {
            "user_input": body.question,
            "route": "",
            "response": "",
        }
        final_state = agent.invoke(initial_state)
        return AgentResponse(
            response=final_state["response"],
            route=final_state.get("route"),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Courses

@app.post("/courses/ask", response_model=CourseResponse, tags=["Cours"])
def courses_ask(body: QuestionRequest):
    """Pose une question à l'agent RAG sur les cours indexés."""
    try:
        from app.agents.course_agent import run_course_agent
        answer = run_course_agent(body.question)
        return CourseResponse(answer=answer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/courses/quiz", response_model=QuizResponse, tags=["Cours"])
def courses_quiz(body: QuizRequest):
    """Génère un QCM sur un thème à partir des cours indexés."""
    try:
        from app.agents.course_agent import generate_quiz
        quiz = generate_quiz(topic=body.topic, nb_questions=body.nb_questions)
        return QuizResponse(quiz=quiz, topic=body.topic, nb_questions=body.nb_questions)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/courses/summary", response_model=SummaryResponse, tags=["Cours"])
def courses_summary(body: SummaryRequest):
    """Génère un résumé structuré d'un concept de cours."""
    try:
        from app.agents.course_agent import summarize_course
        summary = summarize_course(topic=body.topic)
        return SummaryResponse(summary=summary, topic=body.topic)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Internship

@app.post("/internship/search", response_model=InternshipResponse, tags=["Stage"])
def internship_search(body: SearchRequest):
    """Recherche des offres de stage et retourne le scoring IA."""
    try:
        from app.agents.internship_agent import run_internship_search
        result = run_internship_search(body.query)

        if "erreur" in result:
            raise HTTPException(status_code=404, detail=result["erreur"])

        evaluation = result.get("evaluation", {})
        return InternshipResponse(
            query=result["query"],
            score=evaluation.get("score"),
            verdict=evaluation.get("verdict"),
            points_forts=evaluation.get("points_forts", []),
            points_manquants=evaluation.get("points_manquants", []),
            report=result["report"],
            raw_results=result.get("raw_results", "")[:500],
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/internship/cover-letter", response_model=CoverLetterResponse, tags=["Stage"])
def internship_cover_letter(body: CoverLetterRequest):
    """Génère une lettre de motivation personnalisée pour une offre."""
    try:
        from app.agents.internship_agent import generate_cover_letter
        letter = generate_cover_letter(job_description=body.job_description)
        return CoverLetterResponse(letter=letter)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/internship/hr-email", response_model=HrEmailResponse, tags=["Stage"])
def internship_hr_email(body: HrEmailRequest):
    """Génère un email de candidature spontanée pour un poste."""
    try:
        from app.agents.internship_agent import generate_hr_email
        email = generate_hr_email(company=body.company, job_title=body.job_title)
        return HrEmailResponse(email=email)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Planner

@app.post("/planner/study-plan", response_model=StudyPlanResponse, tags=["Planning"])
def planner_study_plan(body: StudyPlanRequest):
    """Génère un plan de révision jour par jour."""
    try:
        from app.agents.planner_agent import generate_study_plan
        plan = generate_study_plan(
            topics=body.topics,
            exam_date=body.exam_date,
            hours_per_day=body.hours_per_day,
        )
        return StudyPlanResponse(plan=plan, exam_date=body.exam_date, topics=body.topics)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/planner/prioritize", response_model=PrioritizeResponse, tags=["Planning"])
def planner_prioritize(body: PrioritizeRequest):
    """Priorise une liste de tâches avec la matrice d'Eisenhower."""
    try:
        from app.agents.planner_agent import prioritize_tasks
        result = prioritize_tasks(tasks=body.tasks)
        return PrioritizeResponse(prioritized=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Memory

@app.get("/memory/history", response_model=HistoryResponse, tags=["Mémoire"])
def memory_history():
    """Retourne l'historique de conversation de la session."""
    from app.memory.storage import get_history
    history = get_history()
    return HistoryResponse(history=history, count=len(history))


@app.post("/memory/clear", tags=["Mémoire"])
def memory_clear():
    """Réinitialise la mémoire de session."""
    from app.memory.storage import clear_memory
    clear_memory()
    return JSONResponse(content={"status": "ok", "message": "Mémoire effacée."})
