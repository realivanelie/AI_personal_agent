from langchain_community.chat_models import ChatOllama
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from app.config import Config
from datetime import datetime


def generate_study_plan(topics: list[str], exam_date: str, hours_per_day: int = 2) -> str:
    """
    Génère un plan de révision personnalisé.
    
    Args:
        topics: Liste des thèmes à réviser
        exam_date: Date de l'examen (format "YYYY-MM-DD")
        hours_per_day: Heures de travail par jour
    """
    today = datetime.now().strftime("%Y-%m-%d")
    topics_str = "\n".join(f"- {t}" for t in topics)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """Tu es un coach académique expert en organisation pédagogique.
        
Génère un plan de révision structuré et réaliste.

Informations :
- Date du jour : {today}
- Date de l'examen : {exam_date}  
- Heures disponibles par jour : {hours_per_day}h
- Thèmes à couvrir :
{topics}

Le plan doit :
 Être organisé jour par jour
 Équilibrer théorie et pratique (exercices)
 Prévoir des révisions de renforcement
 Inclure des pauses et du temps libre
 Finir 2 jours avant l'examen (révision légère + repos)

Format : Tableau jour par jour avec horaires et objectifs.
"""),
        ("human", "Génère mon plan de révision.")
    ])
    
    llm = ChatOllama(
        model=Config.LLM_MODEL,
        base_url=Config.OLLAMA_BASE_URL,
        temperature=0.3
    )
    
    chain = prompt | llm | StrOutputParser()
    
    return chain.invoke({
        "today": today,
        "exam_date": exam_date,
        "hours_per_day": hours_per_day,
        "topics": topics_str
    })


def prioritize_tasks(tasks: list[str]) -> str:
    """Priorise une liste de tâches par urgence et importance (Matrice Eisenhower)."""
    
    tasks_str = "\n".join(f"- {t}" for t in tasks)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """Tu es un expert en productivité et gestion du temps.
        
Analyse ces tâches et organise-les selon la matrice d'Eisenhower :
🔴 Urgent + Important → À faire maintenant
🟡 Important + Pas urgent → À planifier
🟠 Urgent + Pas important → À déléguer ou faire vite
⚪ Pas urgent + Pas important → À éliminer

TÂCHES :
{tasks}

Donne aussi une recommandation sur l'ordre d'exécution optimal pour la journée.
"""),
        ("human", "Priorise mes tâches.")
    ])
    
    llm = ChatOllama(
        model=Config.LLM_MODEL,
        base_url=Config.OLLAMA_BASE_URL,
        temperature=0.2
    )
    
    chain = prompt | llm | StrOutputParser()
    return chain.invoke({"tasks": tasks_str})