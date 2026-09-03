from langchain_community.chat_models import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from app.rag.retriever import retrieve_context
from app.memory.storage import save_exchange
from app.config import Config

# Prompt système du Course Agent
COURSE_SYSTEM_PROMPT = """Tu es un tuteur pédagogique expert spécialisé en Intelligence Artificielle, 
Machine Learning et Deep Learning pour des étudiants de Master.

Tu dois répondre aux questions en te basant UNIQUEMENT sur le contexte de cours fourni.
Si l'information n'est pas dans le contexte, dis-le clairement.

Ton style de réponse :
- Clair et structuré (utilise des listes si pertinent)
- Donne des exemples concrets quand c'est possible
- Indique toujours la source (nom du cours, page)
- Si la question est vague, reformule avant de répondre

CONTEXTE DES COURS :
{context}
"""

def run_course_agent(question: str) -> str:
    """
    Agent RAG qui répond aux questions sur les cours.
    Récupère le contexte depuis ChromaDB et génère une réponse.
    """
    print(f"\n [Course Agent] Question : {question}")
    
    # 1. Récupération du contexte pertinent
    print("   → Recherche dans la base vectorielle...")
    context = retrieve_context(query=question, k=4)
    
    # 2. Construction du prompt
    prompt = ChatPromptTemplate.from_messages([
        ("system", COURSE_SYSTEM_PROMPT),
        ("human", "{question}")
    ])
    
    # 3. Initialisation du LLM
    llm = ChatOllama(
        model=Config.LLM_MODEL,
        base_url=Config.OLLAMA_BASE_URL,
        temperature=0.2
    )
    
    # 4. Chaîne LangChain
    chain = prompt | llm | StrOutputParser()
    
    # 5. Génération de la réponse
    print("   → Génération de la réponse avec Ollama...")
    response = chain.invoke({
        "context": context,
        "question": question
    })
    
    # 6. Sauvegarde en mémoire
    save_exchange(human_msg=question, ai_msg=response)
    
    return response


def generate_quiz(topic: str, nb_questions: int = 3) -> str:
    """Génère un quiz sur un thème à partir des cours."""
    
    context = retrieve_context(query=topic, k=6)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """Tu es un professeur qui crée des QCM pour étudiants en Master IA.
        
Génère exactement {nb_questions} questions à choix multiples sur le thème demandé.
Chaque question doit avoir 4 options (A, B, C, D) et indiquer la bonne réponse à la fin.

CONTEXTE DES COURS :
{context}

Format de réponse :
Q1. [Question]
A) ...
B) ...
C) ...
D) ...
 Réponse : [Lettre] - [Explication courte]
"""),
        ("human", "Génère un quiz sur : {topic}")
    ])
    
    llm = ChatOllama(
        model=Config.LLM_MODEL,
        base_url=Config.OLLAMA_BASE_URL,
        temperature=0.4
    )
    
    chain = prompt | llm | StrOutputParser()
    
    return chain.invoke({
        "context": context,
        "topic": topic,
        "nb_questions": nb_questions
    })


def summarize_course(topic: str) -> str:
    """Génère un résumé structuré d'un chapitre/concept."""
    
    context = retrieve_context(query=topic, k=6)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """Tu es un tuteur expert. Génère un résumé structuré et mémorisable.

CONTEXTE :
{context}

Format du résumé :
##  Concept : [Nom]
### Définition
[1-2 phrases claires]
### Points clés
- [Point 1]
- [Point 2]
- [Point 3]
### Formule / Algorithme clé (si applicable)
[...]
### Application pratique
[Exemple concret]
"""),
        ("human", "Résume le concept : {topic}")
    ])
    
    llm = ChatOllama(
        model=Config.LLM_MODEL,
        base_url=Config.OLLAMA_BASE_URL,
        temperature=0.1
    )
    
    chain = prompt | llm | StrOutputParser()
    return chain.invoke({"context": context, "topic": topic})