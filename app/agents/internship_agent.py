from langchain_community.chat_models import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from app.tools.search import search_internships
from app.tools.scoring import score_job_offer
from app.memory.storage import save_exchange
from app.config import Config
import json


def run_internship_search(query: str) -> dict:
    """
    Workflow complet : Recherche → Scoring → Rapport.
    Retourne un dict avec les résultats bruts et l'évaluation.
    """
    print(f"\n [Internship Agent] Recherche : {query}")
    
    # 1. Recherche web
    print("   → Recherche DuckDuckGo...")
    search_results = search_internships(query)
    
    if not search_results:
        return {"erreur": "Aucune offre trouvée pour cette recherche."}
    
    # 2. Scoring IA
    print("   → Analyse et scoring par Ollama...")
    evaluation = score_job_offer(job_description=search_results)
    
    # 3. Rapport final
    report = format_internship_report(query, search_results, evaluation)
    save_exchange(human_msg=query, ai_msg=report)
    
    return {
        "query": query,
        "raw_results": search_results,
        "evaluation": evaluation,
        "report": report
    }


def format_internship_report(query: str, results: str, evaluation: dict) -> str:
    """Formate le rapport de recherche de stage."""
    score = evaluation.get("score", "N/A")
    points_forts = evaluation.get("points_forts", [])
    points_manquants = evaluation.get("points_manquants", [])
    verdict = evaluation.get("verdict", "N/A")
    
    emoji_verdict = "✅" if verdict == "Postuler" else "❌"
    
    report = f"""
##  Rapport de Recherche de Stage

**Requête :** {query}
**Score de matching :** {score}/100
**Verdict :** {emoji_verdict} {verdict}

###  Points forts matchés
{chr(10).join(f"- {p}" for p in points_forts)}

###  Compétences manquantes
{chr(10).join(f"- {p}" for p in points_manquants)}

###  Résultats bruts
{results[:800]}...
"""
    return report


def generate_cover_letter(job_description: str, profile_path: str = "data/my_profile.txt") -> str:
    """Génère une lettre de motivation personnalisée."""
    
    try:
        with open(profile_path, "r", encoding="utf-8") as f:
            user_profile = f.read()
    except FileNotFoundError:
        user_profile = "Étudiant en Master BIHAR (Big Data & IA) à l'ESTIA, spécialisé en Time Series, XAI et LLM."
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """Tu es un expert en rédaction de lettres de motivation pour des postes en Data Science et IA.
        
Génère une lettre de motivation professionnelle, percutante et personnalisée.
La lettre doit :
- Être en français, ton professionnel mais dynamique
- Mettre en avant les compétences qui matchent l'offre
- Inclure des réalisations concrètes du profil
- Faire maximum 3 paragraphes + formule de politesse
- NE PAS être générique

PROFIL CANDIDAT :
{user_profile}

OFFRE DE STAGE :
{job_description}
"""),
        ("human", "Génère la lettre de motivation.")
    ])
    
    llm = ChatOllama(
        model=Config.LLM_MODEL,
        base_url=Config.OLLAMA_BASE_URL,
        temperature=0.6
    )
    
    chain = prompt | llm | StrOutputParser()
    letter = chain.invoke({
        "user_profile": user_profile,
        "job_description": job_description
    })
    
    save_exchange("Génère une lettre de motivation", letter)
    return letter


def generate_hr_email(company: str, job_title: str, profile_path: str = "data/my_profile.txt") -> str:
    """Génère un email de candidature spontanée pour les RH."""
    
    try:
        with open(profile_path, "r", encoding="utf-8") as f:
            user_profile = f.read()
    except FileNotFoundError:
        user_profile = "Étudiant Master BIHAR ESTIA, spécialisé IA/Data Science."
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """Tu es expert en communication professionnelle.
        
Génère un email de candidature spontanée court et percutant (max 150 mots dans le corps).
Format attendu :
Objet: [...]
Corps: [...]

PROFIL : {user_profile}
"""),
        ("human", "Génère un email de candidature pour le poste de {job_title} chez {company}.")
    ])
    
    llm = ChatOllama(
        model=Config.LLM_MODEL,
        base_url=Config.OLLAMA_BASE_URL,
        temperature=0.5
    )
    
    chain = prompt | llm | StrOutputParser()
    return chain.invoke({
        "user_profile": user_profile,
        "company": company,
        "job_title": job_title
    })