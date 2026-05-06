from ddgs import DDGS

def search_internships(query: str, max_results: int = 5):
    """Cherche des offres de stage sur le web."""
    optimized_query = f"{query} stage alternance offre emploi 2026"

    print(f" Recherche web en cours : {optimized_query}")

    results = []
    with DDGS() as ddgs:
        for r in ddgs.text(optimized_query, max_results=max_results, region="fr-fr"):
            results.append(f"[{r['title']}] {r['body']} ({r['href']})")

    if not results:
        return ""

    return "\n\n".join(results)