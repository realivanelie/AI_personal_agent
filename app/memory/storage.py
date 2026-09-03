from langchain_classic.memory import ConversationBufferWindowMemory
from typing import List, Dict

# Mémoire globale de la session (window = 10 derniers échanges)
_memory = ConversationBufferWindowMemory(
    k=10,
    memory_key="chat_history",
    return_messages=True
)

def get_memory() -> ConversationBufferWindowMemory:
    """Retourne l'objet mémoire de la session."""
    return _memory

def save_exchange(human_msg: str, ai_msg: str):
    """Sauvegarde un échange humain/IA dans la mémoire."""
    _memory.save_context(
        {"input": human_msg},
        {"output": ai_msg}
    )

def get_history() -> List[Dict]:
    """Retourne l'historique de conversation sous forme de liste."""
    messages = _memory.load_memory_variables({}).get("chat_history", [])
    history = []
    for msg in messages:
        role = "user" if msg.type == "human" else "assistant"
        history.append({"role": role, "content": msg.content})
    return history

def clear_memory():
    """Réinitialise la mémoire de session."""
    _memory.clear()
    print("Mémoire effacée.")