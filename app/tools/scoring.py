from langchain_community.chat_models import ChatOllama
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from app.config import Config

def score_job_offer(job_description: str, profile_path: str = "data/my_profile.txt"):
    """Analyse une offre et la note sur 100 par rapport au profil."""
    
    # Lecture de ton profil
    with open(profile_path, "r", encoding="utf-8") as f:
        user_profile = f.read()

    # Initialisation du LLM local (on force le format JSON si supporté, sinon on le guide fortement)
    llm = ChatOllama(model=Config.LLM_MODEL, base_url=Config.OLLAMA_BASE_URL, temperature=0.1, format="json")
    
    parser = JsonOutputParser()
    
    prompt = PromptTemplate(
        template="""Tu es un recruteur expert en Tech et Data Science.
        Analyse l'OFFRE DE STAGE ci-dessous et compare-la au PROFIL du candidat.
        
        PROFIL DU CANDIDAT :
        {user_profile}
        
        OFFRE DE STAGE TROUVÉE :
        {job_description}
        
        Génère une évaluation au format JSON strict avec les clés suivantes :
        - "score" : entier sur 100 représentant le matching technique.
        - "points_forts" : liste de 2 ou 3 compétences du candidat qui matchent bien.
        - "points_manquants" : liste de 1 ou 2 technos demandées que le candidat n'a pas.
        - "verdict" : "Postuler" si score > 75, sinon "Ignorer".
        
        Réponse JSON uniquement :""",
        input_variables=["user_profile", "job_description"],
    )

    chain = prompt | llm | parser
    
    try:
        result = chain.invoke({
            "user_profile": user_profile,
            "job_description": job_description
        })
        return result
    except Exception as e:
        return {"erreur": f"Impossible d'analyser l'offre : {e}"}