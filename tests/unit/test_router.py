"""
Tests unitaires : app/agents/router.py

Teste la logique de routage et de construction du graphe sans appel Ollama.
L'appel LLM dans classify_intent est mocké pour retourner "cours" ou "stage".
"""
import pytest
from unittest.mock import patch, MagicMock
from app.agents.router import (
    AgentState,
    classify_intent,
    route_decision,
    build_agent_graph,
)


# ---------------------------------------------------------------------------
# route_decision : logique pure, pas de mock nécessaire
# ---------------------------------------------------------------------------

class TestRouteDecision:

    def test_routes_to_internship_on_stage(self):
        state: AgentState = {"user_input": "cherche stage", "route": "stage", "response": ""}
        assert route_decision(state) == "internship_node"

    def test_routes_to_course_on_cours(self):
        state: AgentState = {"user_input": "explique ML", "route": "cours", "response": ""}
        assert route_decision(state) == "course_node"

    def test_routes_to_course_on_unknown_route(self):
        """Toute valeur non reconnue doit retourner course_node (fallback)."""
        state: AgentState = {"user_input": "...", "route": "inconnu", "response": ""}
        assert route_decision(state) == "course_node"

    def test_routes_to_course_on_empty_route(self):
        state: AgentState = {"user_input": "...", "route": "", "response": ""}
        assert route_decision(state) == "course_node"


# ---------------------------------------------------------------------------
# classify_intent : mock du LLM
# ---------------------------------------------------------------------------

class TestClassifyIntent:

    def _run_classify(self, llm_output: str, user_input: str) -> AgentState:
        """Helper : mock la chaîne LLM → retourne llm_output."""
        mock_chain = MagicMock()
        mock_chain.invoke.return_value = llm_output

        with patch("app.agents.router.ChatOllama"), \
             patch("app.agents.router.ChatPromptTemplate") as mock_prompt_cls, \
             patch("app.agents.router.StrOutputParser"):

            mock_prompt = MagicMock()
            mock_prompt.__or__ = MagicMock(return_value=mock_chain)
            mock_chain.__or__ = MagicMock(return_value=mock_chain)
            mock_prompt_cls.from_messages.return_value = mock_prompt

            state: AgentState = {"user_input": user_input, "route": "", "response": ""}
            return classify_intent(state)

    def test_classifies_cours_intent(self):
        result = self._run_classify("cours", "Explique-moi la régularisation L2")
        assert result["route"] == "cours"

    def test_classifies_stage_intent(self):
        result = self._run_classify("stage", "Cherche un stage Data Scientist à Paris")
        assert result["route"] == "stage"

    def test_fallback_on_unexpected_output(self):
        """Si le LLM retourne n'importe quoi, fallback sur 'cours'."""
        result = self._run_classify("blabla", "Question quelconque")
        assert result["route"] == "cours"

    def test_strips_whitespace_from_llm_output(self):
        result = self._run_classify("  cours  \n", "Qu'est-ce que le CNN ?")
        assert result["route"] == "cours"

    def test_state_user_input_is_preserved(self):
        user_input = "Ma question de cours"
        result = self._run_classify("cours", user_input)
        assert result["user_input"] == user_input

    def test_stage_with_uppercase_is_normalized(self):
        result = self._run_classify("STAGE", "Lettre de motivation")
        # Le .lower() dans router.py normalise → "stage"
        assert result["route"] == "stage"


# ---------------------------------------------------------------------------
# build_agent_graph
# ---------------------------------------------------------------------------

class TestBuildAgentGraph:

    def test_graph_compiles_without_error(self):
        graph = build_agent_graph()
        assert graph is not None

    def test_graph_is_callable(self):
        graph = build_agent_graph()
        assert callable(graph.invoke)
