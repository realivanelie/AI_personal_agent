from app.tools.search import search_internships
from app.tools.scoring import score_job_offer
import json

def run_internship_test():
    print("💼 --- TEST DU MODULE RECHERCHE DE STAGE ---")
    
    # 1. Recherche d'une offre
    query = "Data Scientist Time Series MLOps"
    print("\nÉtape 1 : Recherche sur le web...")
    search_results = search_internships(query)
    
    print("\nExtraits trouvés par DuckDuckGo :")
    print(search_results[:500] + "...\n")
    
    # 2. Scoring par l'IA
    print("Étape 2 : Analyse et Scoring par Llama 3...")
    evaluation = score_job_offer(job_description=search_results)
    
    # 3. Affichage du résultat formaté
    print("\n📊 RÉSULTAT DE L'ÉVALUATION :")
    print(json.dumps(evaluation, indent=4, ensure_ascii=False))

if __name__ == "__main__":
    run_internship_test()