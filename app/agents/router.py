from typing import TypedDict, Literal
from langgraph.graph import StateGraph, END
from langchain_community.chat_models import ChatOllama
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from app.agents.course_agent import run_course_agent
from app.agents.internship_agent import run_internship_search
from app.config import Config


# 1. Définition de l'état du graphe
class AgentState(TypedDict):
    user_input: str
    route: str          
    response: str


# 2. Nœud : Classifier (Router)
def classify_intent(state: AgentState) -> AgentState:
    """
    Analyse l'intention de l'utilisateur et détermine le routage.
    Retourne "cours" ou "stage".
    """
    user_input = state["user_input"]
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """Tu es un système de routage intelligent pour un agent IA académique.
        
Analyse la question de l'utilisateur et réponds UNIQUEMENT par un seul mot :
- "cours" si la question concerne : les cours, le ML, le DL, les révisions, un concept IA, un quiz, un résumé de chapitre
- "stage" si la question concerne : un stage, une offre d'emploi, une lettre de motivation, un email RH, le scoring d'offre, la recherche d'emploi

Réponds uniquement par "cours" ou "stage", rien d'autre.
"""),
        ("human", "{user_input}")
    ])
    
    llm = ChatOllama(
        model=Config.LLM_MODEL,
        base_url=Config.OLLAMA_BASE_URL,
    )
    
    chain = prompt | llm | StrOutputParser()
    route = chain.invoke({"user_input": user_input}).strip().lower()
    
    # Sécurité : si réponse inattendue, fallback sur "cours"
    if route not in ["cours", "stage"]:
        route = "cours"
    
    print(f"\n🧭 [Router] Intent détecté : '{route}'")
    return {**state, "route": route}


# 3. Nœud : Course Agent
def course_node(state: AgentState) -> AgentState:
    response = run_course_agent(question=state["user_input"])
    return {**state, "response": response}


# 4. Nœud : Internship Agent
def internship_node(state: AgentState) -> AgentState:
    result = run_internship_search(query=state["user_input"])
    response = result.get("report", str(result))
    return {**state, "response": response}


# 5. Fonction de routage conditionnel
def route_decision(state: AgentState) -> Literal["course_node", "internship_node"]:
    if state["route"] == "stage":
        return "internship_node"
    return "course_node"


# 6. Construction du graphe LangGraph
def build_agent_graph():
    """Construit et compile le graphe d'agents LangGraph."""
    
    graph = StateGraph(AgentState)
    
    # Ajout des nœuds
    graph.add_node("router", classify_intent)
    graph.add_node("course_node", course_node)
    graph.add_node("internship_node", internship_node)
    
    # Point d'entrée
    graph.set_entry_point("router")
    
    # Routage conditionnel depuis le router
    graph.add_conditional_edges(
        "router",
        route_decision,
        {
            "course_node": "course_node",
            "internship_node": "internship_node"
        }
    )
    
    # Les deux agents terminent
    graph.add_edge("course_node", END)
    graph.add_edge("internship_node", END)
    
    return graph.compile()


# 7. Fonction principale d'invocation
def run_agent(user_input: str) -> str:
    """Point d'entrée principal : invoque le graphe avec l'input utilisateur."""
    
    agent = build_agent_graph()
    
    initial_state: AgentState = {
        "user_input": user_input,
        "route": "",
        "response": ""
    }
    
    final_state = agent.invoke(initial_state)
    return final_state["response"]