# AI Personal Agent

Agent intelligent multi-modules conçu pour les étudiants en Master IA — automatisation académique, recherche de stage, et planification d'études.

**Projet personnel de Master BIHAR (Big Data & IA) — ESTIA, Bidart**  
Stack : LangGraph · LangChain · Ollama · ChromaDB · FastAPI · Streamlit

---

## Vue d'ensemble

L'AI Personal Agent est un assistant autonome qui orchestre trois modules spécialisés via un graphe d'agents (LangGraph). Il fonctionne **entièrement en local** grâce à Ollama, garantissant la confidentialité des données.

```
                      Entrée utilisateur
                             |
                      Router (LangGraph)
                      Intent classification
                      /        |         \
              [cours]     [stage]     [planning]
                 |            |            |
          Course Agent  Internship   Planner Agent
            (RAG)       Agent (Web)  (Scheduler)
                 |            |            |
            ChromaDB    DuckDuckGo    Markdown plan
```

---

## Fonctionnalités

### Module Cours (RAG)
- Chat avec un tuteur IA sur les cours indexés (PDF, Markdown, TXT)
- Génération de QCM par thème
- Résumés structurés avec points-clés, formules, exemples
- Sources citées (fichier + numéro de page)

### Module Stage & Emploi
- Recherche automatique d'offres via DuckDuckGo
- Score de compatibilité profil/offre (0-100) via analyse LLM
- Identification des compétences correspondantes et manquantes
- Génération de lettres de motivation personnalisées
- Rédaction d'emails de contact RH

### Module Planification
- Génération de plans de révision jour par jour
- Priorisation des tâches par matrice d'Eisenhower (Urgent/Important)
- Exports téléchargeables en Markdown

---

## Architecture du projet

```
ai_personal_agent/
├── app/
│   ├── agents/
│   │   ├── router.py           # LangGraph : classification d'intention
│   │   ├── course_agent.py     # RAG + quiz + résumés
│   │   ├── internship_agent.py # Recherche + scoring + lettres
│   │   └── planner_agent.py    # Plans d'études + Eisenhower
│   ├── rag/
│   │   ├── loader.py           # Ingestion PDF/Markdown/TXT
│   │   ├── splitter.py         # Découpage sémantique
│   │   ├── embeddings.py       # HuggingFace all-MiniLM-L6-v2
│   │   ├── vector_store.py     # ChromaDB (persistant)
│   │   └── retriever.py        # Recherche sémantique (k=4)
│   ├── tools/
│   │   ├── scoring.py          # Analyse offre vs profil → JSON
│   │   └── search.py           # DuckDuckGo wrapper
│   ├── memory/
│   │   └── storage.py          # Historique de session (k=10)
│   └── config.py               # Paramètres centralisés
├── data/
│   ├── pdfs/                   # Supports de cours (~17 PDFs, 95 Mo)
│   ├── vector_store/           # Base vectorielle ChromaDB (auto-créée)
│   └── my_profile.txt          # CV utilisateur pour le matching stage
├── tests/
│   ├── test_internship_module.py
│   └── test_ollama_rag.py
├── main.py                     # Interface CLI
├── streamlit_app.py            # Interface Web (Streamlit)
├── check_machine.py            # Diagnostic système + recommandations modèles
├── debug_rag_v2.py             # Diagnostic pipeline RAG
├── requirements.txt
└── .env
```

---

## Stack technique

| Composant | Technologie | Notes |
|---|---|---|
| Orchestration agentique | LangGraph 0.0.40 | État TypedDict, routage conditionnel |
| Framework LLM | LangChain 1.0.5 | Chaînes, mémoire, prompts |
| LLM local | Ollama (Qwen 2.5-Coder 7B / Llama 3) | localhost:11434 |
| LLM cloud (optionnel) | DeepSeek API v3 | Fallback via `.env` |
| Embeddings | HuggingFace all-MiniLM-L6-v2 | 384 dimensions, CPU-friendly |
| Base vectorielle | ChromaDB 0.4.24 | Persistant dans `data/vector_store/` |
| Interface | Streamlit 1.33.0 | Thème dark custom, 5 modules |
| Recherche web | DuckDuckGo Search API | Sans clé API |
| Parsing PDF | PyPDF 4.2.0 | + TextLoader pour Markdown/TXT |

---

## Installation

### Prérequis

- Python 3.10+
- [Ollama](https://ollama.ai) installé et démarré
- 8 Go RAM minimum (16 Go recommandé pour Qwen 7B)

### Étapes

```bash
# 1. Cloner le projet
git clone https://github.com/realivanelie/ai_personal_agent.git
cd ai_personal_agent

# 2. Environnement Python
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 3. Télécharger le modèle Ollama
ollama pull qwen2.5-coder:7b   # modèle par défaut (config.py)
# ou
ollama pull llama3              # alternative

# 4. Variables d'environnement (optionnel, pour DeepSeek)
cp .env.example .env
# Éditer .env :
# DEEPSEEK_API_KEY=votre_clef
# DEEPSEEK_BASE_URL=https://api.deepseek.com
```

### Lancement

```bash
# Interface Web (recommandé)
streamlit run streamlit_app.py

# Interface CLI
python main.py

# Diagnostic système
python check_machine.py

# Diagnostic RAG
python debug_rag_v2.py
```

L'interface Web sera disponible sur `http://localhost:8501`.

---

## Utilisation

### Premier lancement

1. Déposer vos PDFs de cours dans `data/pdfs/`
2. Dans l'onglet **Config**, cliquer sur "Réindexer les documents"
3. La base vectorielle est créée automatiquement dans `data/vector_store/`

### Module Cours

```
Utilisateur : "Explique-moi la régularisation L2 en machine learning"
→ Router classifie "cours"
→ Course Agent récupère les chunks pertinents depuis ChromaDB
→ Ollama génère une réponse avec citations (fichier + page)
```

### Module Stage

```
Utilisateur : "Stage Data Scientist MLOps Paris 2026"
→ DuckDuckGo recherche des offres
→ Ollama score le profil vs offre → JSON {score, points_forts, verdict}
→ Génération lettre de motivation ou email RH disponible
```

### Module Planning

```
Utilisateur : liste les topics d'exam + heures/jour disponibles
→ Ollama génère un planning jour par jour téléchargeable
```

---

## Configuration

Le fichier `app/config.py` centralise les paramètres :

```python
class Config:
    LLM_MODEL = "qwen2.5-coder:7b"   # Modèle Ollama
    OLLAMA_BASE_URL = "http://localhost:11434"
    DATA_DIR = "data/pdfs"
    VECTOR_STORE_DIR = "data/vector_store"
    CHUNK_SIZE = 1000
    CHUNK_OVERLAP = 150
```

Pour changer de modèle, modifier `LLM_MODEL` (ex: `"llama3"`, `"mistral"`).  
Pour connaître le modèle adapté à votre machine : `python check_machine.py`

---

## Contenu indexé

Le projet inclut 17 PDFs de cours (~95 Mo) couvrant :

- Machine Learning I & II (5 + 4 chapitres)
- Deep Learning : NLP, CNN, RNN, Transfer Learning
- MLOps
- Apache Airflow

---

## API REST (FastAPI)

L'agent expose une API REST complète, documentée automatiquement via Swagger UI.

### Lancement

```bash
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

- Swagger UI : `http://localhost:8000/docs`
- ReDoc : `http://localhost:8000/redoc`

### Endpoints

| Méthode | Endpoint | Tag | Description |
|---|---|---|---|
| `GET` | `/health` | Monitoring | Statut du service + modèle actif |
| `POST` | `/agent/ask` | Agent | Routage automatique cours / stage |
| `POST` | `/courses/ask` | Cours | Question RAG sur les cours indexés |
| `POST` | `/courses/quiz` | Cours | Génération de QCM par thème |
| `POST` | `/courses/summary` | Cours | Résumé structuré d'un concept |
| `POST` | `/internship/search` | Stage | Recherche + scoring d'offres |
| `POST` | `/internship/cover-letter` | Stage | Lettre de motivation personnalisée |
| `POST` | `/internship/hr-email` | Stage | Email de candidature spontanée |
| `POST` | `/planner/study-plan` | Planning | Plan de révision jour par jour |
| `POST` | `/planner/prioritize` | Planning | Priorisation Eisenhower des tâches |
| `GET` | `/memory/history` | Mémoire | Historique de la session |
| `POST` | `/memory/clear` | Mémoire | Réinitialisation de la mémoire |

### Exemples de requêtes

```bash
# Santé
curl http://localhost:8000/health

# Question à l'agent (routage automatique)
curl -X POST http://localhost:8000/agent/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "Explique le gradient descent"}'

# QCM sur les réseaux de neurones
curl -X POST http://localhost:8000/courses/quiz \
  -H "Content-Type: application/json" \
  -d '{"topic": "réseaux de neurones", "nb_questions": 3}'

# Recherche de stage avec scoring
curl -X POST http://localhost:8000/internship/search \
  -H "Content-Type: application/json" \
  -d '{"query": "Data Scientist MLOps Paris"}'

# Plan de révision
curl -X POST http://localhost:8000/planner/study-plan \
  -H "Content-Type: application/json" \
  -d '{"topics": ["Machine Learning", "Deep Learning"], "exam_date": "2026-06-01", "hours_per_day": 3}'
```

### Structure de l'API

```
api/
├── main.py      # Définition des routes FastAPI
└── schemas.py   # Modèles Pydantic (requêtes + réponses)
```

Les schémas Pydantic garantissent la validation des entrées et la documentation automatique des contrats de données dans Swagger UI.

---

## Roadmap

- [ ] Intégration Google Calendar pour synchroniser les plans de révision
- [ ] Agent Critique pour auto-corriger les lettres de motivation
- [ ] Déploiement Docker pour stack MLOps complète
- [ ] Monitoring des traces avec LangSmith

---

## Auteur

**Ivan Elie DJAKPA**  
Étudiant en Master of Science BIHAR (Big Data & IA) — ESTIA, Bidart  
Spécialisé en Time Series, XAI et Ingénierie des LLM
