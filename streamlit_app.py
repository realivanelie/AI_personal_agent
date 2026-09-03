"""
AI Personal Agent — Interface Streamlit
BIHAR ESTIA — Djakpa Ivan Elie DJALEGA
"""

import streamlit as st
import json
import time
import os
from datetime import datetime

# ──────────────────────────────────────────────────────────────
# CONFIG PAGE
# ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Personal Agent ",
    page_icon="⬡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ──────────────────────────────────────────────────────────────
# GLOBAL CSS
# ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:ital,wght@0,400;0,700;1,400&family=Syne:wght@400;600;700;800&display=swap');

/* ── ROOT VARIABLES ── */
:root {
    --bg-0:   #080c12;
    --bg-1:   #0d1421;
    --bg-2:   #111c2e;
    --bg-3:   #172338;
    --cyan:   #00d4ff;
    --cyan2:  #00a8cc;
    --green:  #00ff88;
    --amber:  #ffb347;
    --red:    #ff4757;
    --muted:  #3d5a7a;
    --text:   #c8dff5;
    --text2:  #7a9cc0;
    --border: rgba(0, 212, 255, 0.12);
    --glow:   0 0 24px rgba(0,212,255,0.15);
}

/* ── GLOBAL ── */
html, body, [class*="css"] {
    font-family: 'Syne', sans-serif !important;
    background-color: var(--bg-0) !important;
    color: var(--text) !important;
}

.stApp {
    background-color: var(--bg-0) !important;
    background-image:
        radial-gradient(ellipse 80% 40% at 50% -10%, rgba(0,212,255,0.06) 0%, transparent 70%),
        radial-gradient(ellipse 40% 30% at 90% 80%, rgba(0,255,136,0.04) 0%, transparent 60%);
}

/* ── SIDEBAR ── */
section[data-testid="stSidebar"] {
    background: var(--bg-1) !important;
    border-right: 1px solid var(--border) !important;
}

section[data-testid="stSidebar"] > div {
    padding: 0 !important;
}

/* ── HIDE STREAMLIT CHROME ── */
#MainMenu, footer, header { visibility: hidden; }
.stDeployButton { display: none; }

/* ── BUTTONS ── */
.stButton > button {
    background: transparent !important;
    border: 1px solid var(--cyan) !important;
    color: var(--cyan) !important;
    font-family: 'Space Mono', monospace !important;
    font-size: 12px !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
    border-radius: 4px !important;
    padding: 8px 20px !important;
    transition: all 0.2s ease !important;
    box-shadow: inset 0 0 0 0 var(--cyan) !important;
}
.stButton > button:hover {
    background: rgba(0,212,255,0.08) !important;
    box-shadow: 0 0 16px rgba(0,212,255,0.25) !important;
    transform: translateY(-1px) !important;
}
.stButton > button:active {
    transform: translateY(0) !important;
}

/* ── INPUTS ── */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stNumberInput > div > div > input {
    background: var(--bg-2) !important;
    border: 1px solid var(--border) !important;
    border-radius: 4px !important;
    color: var(--text) !important;
    font-family: 'Space Mono', monospace !important;
    font-size: 13px !important;
    transition: border 0.2s !important;
}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: var(--cyan) !important;
    box-shadow: 0 0 0 1px var(--cyan) !important;
}

/* ── SELECT BOXES ── */
.stSelectbox > div > div {
    background: var(--bg-2) !important;
    border: 1px solid var(--border) !important;
    border-radius: 4px !important;
    color: var(--text) !important;
}

/* ── SLIDERS ── */
.stSlider > div > div > div > div {
    background: var(--cyan) !important;
}

/* ── EXPANDER ── */
.streamlit-expanderHeader {
    background: var(--bg-2) !important;
    border: 1px solid var(--border) !important;
    border-radius: 4px !important;
    color: var(--cyan) !important;
    font-family: 'Space Mono', monospace !important;
    font-size: 12px !important;
}

/* ── SPINNER ── */
.stSpinner > div {
    border-top-color: var(--cyan) !important;
}

/* ── METRICS ── */
[data-testid="stMetric"] {
    background: var(--bg-2) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    padding: 16px !important;
}
[data-testid="stMetricValue"] {
    color: var(--cyan) !important;
    font-family: 'Space Mono', monospace !important;
}
[data-testid="stMetricLabel"] {
    color: var(--text2) !important;
    font-size: 11px !important;
    text-transform: uppercase !important;
    letter-spacing: 0.1em !important;
}

/* ── DIVIDER ── */
hr {
    border: none !important;
    border-top: 1px solid var(--border) !important;
    margin: 24px 0 !important;
}

/* ── TABS ── */
.stTabs [data-baseweb="tab-list"] {
    background: transparent !important;
    border-bottom: 1px solid var(--border) !important;
    gap: 0 !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: var(--text2) !important;
    font-family: 'Space Mono', monospace !important;
    font-size: 11px !important;
    text-transform: uppercase !important;
    letter-spacing: 0.1em !important;
    border-bottom: 2px solid transparent !important;
    padding: 12px 20px !important;
    transition: all 0.2s !important;
}
.stTabs [aria-selected="true"] {
    color: var(--cyan) !important;
    border-bottom-color: var(--cyan) !important;
    background: transparent !important;
}

/* ── CODE BLOCKS ── */
.stCodeBlock, code {
    background: var(--bg-1) !important;
    border: 1px solid var(--border) !important;
    font-family: 'Space Mono', monospace !important;
}

/* ── SUCCESS / WARNING / ERROR ── */
.stSuccess { background: rgba(0,255,136,0.06) !important; border-left-color: var(--green) !important; }
.stWarning { background: rgba(255,179,71,0.06) !important; border-left-color: var(--amber) !important; }
.stError   { background: rgba(255,71,87,0.06)  !important; border-left-color: var(--red)   !important; }
.stInfo    { background: rgba(0,212,255,0.06)   !important; border-left-color: var(--cyan)  !important; }

/* ── RADIO / CHECKBOX ── */
[data-testid="stRadio"] label, [data-testid="stCheckbox"] label {
    color: var(--text) !important;
    font-size: 13px !important;
}
</style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────
# COMPONENT HELPERS
# ──────────────────────────────────────────────────────────────

def card(title: str, content: str, icon: str = "⬡", color: str = "cyan"):
    colors = {"cyan": "#00d4ff", "green": "#00ff88", "amber": "#ffb347", "red": "#ff4757"}
    c = colors.get(color, "#00d4ff")
    st.markdown(f"""
    <div style="
        background: #111c2e;
        border: 1px solid {c}22;
        border-left: 3px solid {c};
        border-radius: 8px;
        padding: 20px 24px;
        margin: 8px 0;
        box-shadow: 0 4px 24px rgba(0,0,0,0.3);
    ">
        <div style="display:flex; align-items:center; gap:10px; margin-bottom:10px;">
            <span style="font-size:18px;">{icon}</span>
            <span style="color:{c}; font-family:'Space Mono',monospace; font-size:11px;
                         text-transform:uppercase; letter-spacing:0.1em; font-weight:700;">
                {title}
            </span>
        </div>
        <div style="color:#c8dff5; font-size:14px; line-height:1.7;">{content}</div>
    </div>
    """, unsafe_allow_html=True)


def response_bubble(text: str, role: str = "ai"):
    if role == "user":
        bg, border, align, label = "#172338", "#3d5a7a", "flex-end", "VOUS"
        c = "#7a9cc0"
    else:
        bg, border, align, label = "#0d1f35", "#00d4ff33", "flex-start", "AGENT IA"
        c = "#00d4ff"

    escaped = text.replace("\n", "<br>").replace("`", "&#96;")
    st.markdown(f"""
    <div style="display:flex; justify-content:{align}; margin:8px 0;">
        <div style="
            max-width:82%;
            background:{bg};
            border:1px solid {border};
            border-radius:8px;
            padding:14px 18px;
        ">
            <div style="color:{c}; font-family:'Space Mono',monospace;
                        font-size:9px; text-transform:uppercase;
                        letter-spacing:0.12em; margin-bottom:8px; opacity:0.8;">
                {label}
            </div>
            <div style="color:#c8dff5; font-size:13px; line-height:1.75;">
                {escaped}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def section_header(title: str, subtitle: str = ""):
    st.markdown(f"""
    <div style="margin-bottom:24px;">
        <h2 style="
            font-family:'Syne',sans-serif;
            font-weight:800;
            font-size:22px;
            color:#c8dff5;
            margin:0 0 4px 0;
            letter-spacing:-0.01em;
        ">{title}</h2>
        <p style="color:#3d5a7a; font-family:'Space Mono',monospace;
                  font-size:11px; margin:0; text-transform:uppercase; letter-spacing:0.1em;">
            {subtitle}
        </p>
        <div style="width:40px; height:2px; background:linear-gradient(90deg,#00d4ff,transparent);
                    margin-top:10px; border-radius:2px;"></div>
    </div>
    """, unsafe_allow_html=True)


def badge(text: str, color: str = "cyan"):
    colors = {"cyan": "#00d4ff", "green": "#00ff88", "amber": "#ffb347", "red": "#ff4757", "muted": "#3d5a7a"}
    c = colors.get(color, "#00d4ff")
    st.markdown(f"""
    <span style="
        display:inline-block;
        background:{c}18;
        border:1px solid {c}55;
        color:{c};
        font-family:'Space Mono',monospace;
        font-size:10px;
        text-transform:uppercase;
        letter-spacing:0.1em;
        padding:3px 10px;
        border-radius:3px;
        margin:2px;
    ">{text}</span>
    """, unsafe_allow_html=True)


def score_gauge(score: int):
    color = "#00ff88" if score >= 75 else "#ffb347" if score >= 50 else "#ff4757"
    verdict = "POSTULER ✓" if score >= 75 else "BORDERLINE" if score >= 50 else "IGNORER ✗"
    pct = score
    st.markdown(f"""
    <div style="background:#111c2e; border:1px solid #00d4ff22; border-radius:8px; padding:24px; text-align:center;">
        <div style="position:relative; display:inline-block; width:140px; height:140px;">
            <svg viewBox="0 0 140 140" width="140" height="140">
                <circle cx="70" cy="70" r="54" fill="none" stroke="#172338" stroke-width="10"/>
                <circle cx="70" cy="70" r="54" fill="none" stroke="{color}" stroke-width="10"
                    stroke-dasharray="{2*3.14159*54*pct/100:.1f} {2*3.14159*54*(100-pct)/100:.1f}"
                    stroke-dashoffset="{2*3.14159*54*0.25:.1f}"
                    stroke-linecap="round"
                    style="transition: stroke-dasharray 1s ease;"/>
                <text x="70" y="65" text-anchor="middle"
                      fill="{color}" font-family="Space Mono" font-size="26" font-weight="700">{score}</text>
                <text x="70" y="84" text-anchor="middle"
                      fill="#3d5a7a" font-family="Space Mono" font-size="11">/100</text>
            </svg>
        </div>
        <div style="color:{color}; font-family:'Space Mono',monospace; font-size:13px;
                    font-weight:700; letter-spacing:0.12em; margin-top:8px;">{verdict}</div>
    </div>
    """, unsafe_allow_html=True)


# ──────────────────────────────────────────────────────────────
# SESSION STATE INIT
# ──────────────────────────────────────────────────────────────
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "vector_db_ready" not in st.session_state:
    st.session_state.vector_db_ready = False
if "active_module" not in st.session_state:
    st.session_state.active_module = "home"
if "last_evaluation" not in st.session_state:
    st.session_state.last_evaluation = None
if "cover_letter" not in st.session_state:
    st.session_state.cover_letter = ""
if "hr_email" not in st.session_state:
    st.session_state.hr_email = ""
if "study_plan" not in st.session_state:
    st.session_state.study_plan = ""

# ──────────────────────────────────────────────────────────────
# AGENT LOADERS (avec fallback si modules non disponibles)
# ──────────────────────────────────────────────────────────────

@st.cache_resource(show_spinner=False)
def load_vector_db():
    try:
        from app.rag.loader import ingest_course_pdfs
        from app.rag.vector_store import build_vector_db, get_vector_store
        from app.config import Config
        import os
        if os.path.exists(Config.VECTOR_STORE_DIR) and os.listdir(Config.VECTOR_STORE_DIR):
            return get_vector_store(), "existing"
        chunks = ingest_course_pdfs()
        if not chunks:
            return None, "no_pdfs"
        db = build_vector_db(chunks)
        return db, "built"
    except Exception as e:
        return None, f"error:{e}"


def call_course_agent(question: str) -> str:
    try:
        from app.agents.course_agent import run_course_agent
        return run_course_agent(question)
    except Exception as e:
        return f"⚠️ Erreur Course Agent : {e}\n\nVérifiez qu'Ollama est lancé (`ollama serve`) et que la base vectorielle est initialisée."


def call_quiz_agent(topic: str, n: int) -> str:
    try:
        from app.agents.course_agent import generate_quiz
        return generate_quiz(topic, nb_questions=n)
    except Exception as e:
        return f"⚠️ Erreur génération quiz : {e}"


def call_summary_agent(topic: str) -> str:
    try:
        from app.agents.course_agent import summarize_course
        return summarize_course(topic)
    except Exception as e:
        return f"⚠️ Erreur résumé : {e}"


def call_internship_search(query: str) -> dict:
    try:
        from app.agents.internship_agent import run_internship_search
        return run_internship_search(query)
    except Exception as e:
        return {"erreur": str(e), "report": f"⚠️ Erreur : {e}"}


def call_cover_letter(job_desc: str) -> str:
    try:
        from app.agents.internship_agent import generate_cover_letter
        return generate_cover_letter(job_desc)
    except Exception as e:
        return f"⚠️ Erreur lettre de motivation : {e}"


def call_hr_email(company: str, title: str) -> str:
    try:
        from app.agents.internship_agent import generate_hr_email
        return generate_hr_email(company, title)
    except Exception as e:
        return f"⚠️ Erreur email RH : {e}"


def call_study_plan(topics: list, exam_date: str, hours: int) -> str:
    try:
        from app.agents.planner_agent import generate_study_plan
        return generate_study_plan(topics, exam_date, hours)
    except Exception as e:
        return f"⚠️ Erreur plan de révision : {e}"


def call_prioritize(tasks: list) -> str:
    try:
        from app.agents.planner_agent import prioritize_tasks
        return prioritize_tasks(tasks)
    except Exception as e:
        return f"⚠️ Erreur priorisation : {e}"


# ──────────────────────────────────────────────────────────────
# SIDEBAR
# ──────────────────────────────────────────────────────────────

with st.sidebar:
    # Logo / Brand
    st.markdown("""
    <div style="padding:28px 24px 20px; border-bottom:1px solid rgba(0,212,255,0.1);">
        <div style="display:flex; align-items:center; gap:12px;">
            <div style="
                width:38px; height:38px;
                background:linear-gradient(135deg, #00d4ff22, #00ff8811);
                border:1px solid #00d4ff44;
                border-radius:8px;
                display:flex; align-items:center; justify-content:center;
                font-size:20px;
            ">⬡</div>
            <div>
                <div style="font-family:'Syne',sans-serif; font-weight:800;
                            font-size:15px; color:#c8dff5; letter-spacing:-0.01em;">
                    AI Agent
                </div>
                <div style="font-family:'Space Mono',monospace; font-size:9px;
                            color:#3d5a7a; text-transform:uppercase; letter-spacing:0.12em;">
                    BIHAR · ESTIA
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    # Navigation
    nav_items = [
        ("🏠", "Accueil",  "home"),
        ("📚", "Cours & RAG", "cours"),
        ("💼", "Recherche Stage", "stage"),
        ("📅", "Planificateur", "planner"),
        ("⚙️", "Configuration", "config"),
    ]

    for icon, label, key in nav_items:
        active = st.session_state.active_module == key
        if st.sidebar.button(
            f"{icon}  {label}",
            key=f"nav_{key}",
            use_container_width=True,
        ):
            st.session_state.active_module = key
            st.rerun()

    # VDB Status
    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
    st.markdown("""<div style="padding:0 16px;">
        <div style="font-family:'Space Mono',monospace; font-size:9px;
                    text-transform:uppercase; letter-spacing:0.1em; color:#3d5a7a;
                    margin-bottom:10px;">Statut Système</div>
    </div>""", unsafe_allow_html=True)

    # Ollama status
    ollama_ok = True
    try:
        import httpx
        r = httpx.get("http://localhost:11434/api/tags", timeout=2)
        ollama_ok = r.status_code == 200
    except Exception:
        ollama_ok = False

    status_color = "#00ff88" if ollama_ok else "#ff4757"
    status_label = "Ollama · En ligne" if ollama_ok else "Ollama · Hors ligne"

    st.markdown(f"""
    <div style="margin:0 16px 8px; padding:10px 14px;
                background:#0d1421; border:1px solid rgba(0,212,255,0.08); border-radius:6px;">
        <div style="display:flex; align-items:center; gap:8px;">
            <div style="width:6px;height:6px;border-radius:50%;background:{status_color};
                        box-shadow: 0 0 6px {status_color};"></div>
            <span style="font-family:'Space Mono',monospace; font-size:10px; color:#7a9cc0;">
                {status_label}
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    vdb_color = "#00ff88" if st.session_state.vector_db_ready else "#ffb347"
    vdb_label = "ChromaDB · Prêt" if st.session_state.vector_db_ready else "ChromaDB · En attente"
    st.markdown(f"""
    <div style="margin:0 16px 8px; padding:10px 14px;
                background:#0d1421; border:1px solid rgba(0,212,255,0.08); border-radius:6px;">
        <div style="display:flex; align-items:center; gap:8px;">
            <div style="width:6px;height:6px;border-radius:50%;background:{vdb_color};
                        box-shadow: 0 0 6px {vdb_color};"></div>
            <span style="font-family:'Space Mono',monospace; font-size:10px; color:#7a9cc0;">
                {vdb_label}
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Profile info
    st.markdown("""
    <div style="position:absolute; bottom:0; left:0; right:0;
                padding:16px 20px; border-top:1px solid rgba(0,212,255,0.08);">
        <div style="font-family:'Syne',sans-serif; font-weight:700; font-size:13px; color:#c8dff5;">
            Ivan Elie Djalega
        </div>
        <div style="font-family:'Space Mono',monospace; font-size:9px; color:#3d5a7a;
                    text-transform:uppercase; letter-spacing:0.1em; margin-top:2px;">
            MSc BIHAR · Stage dès Avril 2026
        </div>
    </div>
    """, unsafe_allow_html=True)


# ──────────────────────────────────────────────────────────────
# PAGES
# ──────────────────────────────────────────────────────────────

module = st.session_state.active_module

# ── PAGE : ACCUEIL ───────────────────────────────────────────
if module == "home":
    st.markdown("""
    <div style="padding:40px 0 32px;">
        <div style="font-family:'Space Mono',monospace; font-size:11px; color:#3d5a7a;
                    text-transform:uppercase; letter-spacing:0.2em; margin-bottom:14px;">
            MSc Big Data & IA · ESTIA Bidart
        </div>
        <h1 style="font-family:'Syne',sans-serif; font-weight:800; font-size:42px;
                   color:#c8dff5; margin:0; letter-spacing:-0.03em; line-height:1.1;">
            AI Personal<br>
            <span style="background:linear-gradient(90deg,#00d4ff,#00ff88);
                         -webkit-background-clip:text; -webkit-text-fill-color:transparent;">
                Agent
            </span>
        </h1>
        <p style="color:#7a9cc0; font-size:15px; margin-top:16px; max-width:520px; line-height:1.7;">
            Système d'IA agentique orchestré par <strong style="color:#00d4ff;">LangGraph</strong>.
            Gestion intelligente des cours via <strong style="color:#00d4ff;">RAG</strong>
            et optimisation de la recherche de stage par matching IA.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Stats row
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Modèle LLM", "Llama 3", "Local · Ollama")
    with col2:
        st.metric("Embeddings", "MiniLM-L6", "HuggingFace")
    with col3:
        st.metric("Vector DB", "ChromaDB", "Persisté")
    with col4:
        st.metric("Framework", "LangGraph", "Multi-agents")

    st.markdown("---")

    # Feature cards
    col1, col2, col3 = st.columns(3)
    with col1:
        card(
            "Module Cours · RAG",
            "Posez des questions sur vos cours ML/DL, générez des quiz personnalisés et obtenez des résumés structurés depuis vos PDFs indexés.",
            "📚", "cyan"
        )
    with col2:
        card(
            "Module Stage , Alternance · Matching",
            "Recherche automatisée d'offres, scoring de compatibilité IA sur 100, génération de lettres de motivation et emails RH personnalisés.",
            "💼", "green"
        )
    with col3:
        card(
            "Planificateur · Agentique",
            "Planification de révisions personnalisée avec date d'examen, priorisation de tâches selon la matrice Eisenhower.",
            "📅", "amber"
        )

    st.markdown("---")

    # Architecture diagram text
    st.markdown("""
    <div style="background:#0d1421; border:1px solid rgba(0,212,255,0.1); border-radius:8px;
                padding:24px; font-family:'Space Mono',monospace;">
        <div style="color:#3d5a7a; font-size:10px; text-transform:uppercase;
                    letter-spacing:0.12em; margin-bottom:16px;">Architecture LangGraph</div>
        <div style="color:#7a9cc0; font-size:12px; line-height:2.2;">
            <span style="color:#00d4ff;">User Input</span>
            &nbsp;→&nbsp;
            <span style="color:#00d4ff;">Router Agent</span>
            &nbsp;→&nbsp;
            <span style="color:#c8dff5;">[Intent Classification]</span>
            <br>
            &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
            &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
            ↙&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;↘
            <br>
            &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
            <span style="color:#00ff88;">Course Agent</span>
            &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
            <span style="color:#ffb347;">Internship Agent</span>
            <br>
            &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
            <span style="color:#3d5a7a;">↓ ChromaDB RAG</span>
            &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
            <span style="color:#3d5a7a;">↓ DuckDuckGo + Scoring</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Quick start
    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        if st.button("→  Démarrer les Cours", use_container_width=True):
            st.session_state.active_module = "cours"
            st.rerun()
    with col2:
        if st.button("→  Chercher un Stage", use_container_width=True):
            st.session_state.active_module = "stage"
            st.rerun()


# ── PAGE : COURS ─────────────────────────────────────────────
elif module == "cours":
    section_header("Module Cours · RAG", "Retrieval Augmented Generation · Llama 3 Local")

    # Init VDB
    if not st.session_state.vector_db_ready:
        with st.spinner("Initialisation de la base vectorielle..."):
            db, status = load_vector_db()
            if db is not None:
                st.session_state.vector_db_ready = True
                st.success(f"✓ Base vectorielle chargée ({status})")
            elif "no_pdfs" in str(status):
                st.warning("Aucun PDF trouvé dans `data/pdfs/`. Placez vos cours puis relancez.")
            else:
                st.error(f"Erreur d'initialisation : {status}")

    tab1, tab2, tab3 = st.tabs(["💬  Chat RAG", "📝  Générateur de Quiz", "📖  Résumé de Cours"])

    # ── TAB 1 : CHAT ──
    with tab1:
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

        # Affichage de l'historique
        chat_container = st.container()
        with chat_container:
            if not st.session_state.chat_history:
                st.markdown("""
                <div style="text-align:center; padding:40px; color:#3d5a7a;">
                    <div style="font-size:32px; margin-bottom:12px;">💬</div>
                    <div style="font-family:'Space Mono',monospace; font-size:11px;
                                text-transform:uppercase; letter-spacing:0.1em;">
                        Posez une question sur vos cours ML / Deep Learning
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                for msg in st.session_state.chat_history:
                    response_bubble(msg["content"], msg["role"])

        st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

        # Suggestions rapides
        st.markdown("<div style='color:#3d5a7a; font-family:Space Mono,monospace; font-size:10px; text-transform:uppercase; letter-spacing:0.1em; margin-bottom:8px;'>Suggestions</div>", unsafe_allow_html=True)
        sugg_cols = st.columns(3)
        suggestions = [
            "Explique le Gradient Boosting",
            "Différence LSTM vs Transformer",
            "Comment fonctionne le RAG ?",
        ]
        for i, (col, sugg) in enumerate(zip(sugg_cols, suggestions)):
            with col:
                if st.button(sugg, key=f"sugg_{i}", use_container_width=True):
                    st.session_state.chat_history.append({"role": "user", "content": sugg})
                    with st.spinner("Recherche dans vos cours..."):
                        response = call_course_agent(sugg)
                    st.session_state.chat_history.append({"role": "ai", "content": response})
                    st.rerun()

        # Input
        col_input, col_send, col_clear = st.columns([6, 1, 1])
        with col_input:
            user_q = st.text_input(
                "question",
                placeholder="Ex: Explique le mécanisme d'attention dans les Transformers...",
                label_visibility="collapsed",
                key="cours_input"
            )
        with col_send:
            send = st.button("Envoyer", use_container_width=True, key="send_cours")
        with col_clear:
            if st.button("Effacer", use_container_width=True, key="clear_cours"):
                st.session_state.chat_history = []
                st.rerun()

        if send and user_q.strip():
            st.session_state.chat_history.append({"role": "user", "content": user_q})
            with st.spinner("Analyse en cours..."):
                response = call_course_agent(user_q)
            st.session_state.chat_history.append({"role": "ai", "content": response})
            st.rerun()

    # ── TAB 2 : QUIZ ──
    with tab2:
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        col1, col2 = st.columns([3, 1])
        with col1:
            quiz_topic = st.text_input(
                "Thème du quiz",
                placeholder="Ex: Réseaux de neurones convolutifs (CNN)",
                key="quiz_topic"
            )
        with col2:
            nb_q = st.number_input("Nombre de questions", min_value=1, max_value=10, value=3, key="nb_q")

        if st.button("⚡ Générer le Quiz", use_container_width=False, key="gen_quiz"):
            if quiz_topic.strip():
                with st.spinner(f"Génération de {nb_q} questions sur « {quiz_topic} »..."):
                    quiz = call_quiz_agent(quiz_topic, nb_q)
                card("Quiz Généré", quiz.replace("\n", "<br>"), "📝", "cyan")
            else:
                st.warning("Entrez un thème pour générer le quiz.")

    # ── TAB 3 : RÉSUMÉ ──
    with tab3:
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        summary_topic = st.text_input(
            "Concept ou chapitre à résumer",
            placeholder="Ex: Backpropagation et descente de gradient",
            key="summary_topic"
        )
        if st.button("📖 Générer le Résumé", key="gen_summary"):
            if summary_topic.strip():
                with st.spinner(f"Résumé de « {summary_topic} » en cours..."):
                    summary = call_summary_agent(summary_topic)
                card("Résumé Structuré", summary.replace("\n", "<br>"), "📖", "green")
            else:
                st.warning("Entrez un concept à résumer.")


# ── PAGE : STAGE ─────────────────────────────────────────────
elif module == "stage":
    section_header("Module Stage · Matching IA", "Recherche · Scoring · Candidature Personnalisée")

    tab1, tab2, tab3 = st.tabs(["🔍  Recherche & Scoring", "✉️  Lettre de Motivation", "📧  Email RH"])

    # ── TAB 1 : RECHERCHE ──
    with tab1:
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

        # Exemples de requêtes
        st.markdown("<div style='color:#3d5a7a; font-family:Space Mono,monospace; font-size:10px; text-transform:uppercase; letter-spacing:0.1em; margin-bottom:8px;'>Requêtes suggérées</div>", unsafe_allow_html=True)
        quick_cols = st.columns(3)
        quick_queries = [
            "Data Scientist MLOps stage Paris",
            "AI Engineer LangChain LLM Bordeaux",
            "Data Engineer Spark Airflow Île-de-France",
        ]
        for i, (col, q) in enumerate(zip(quick_cols, quick_queries)):
            with col:
                if st.button(q, key=f"quick_{i}", use_container_width=True):
                    st.session_state["internship_query"] = q

        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        search_query = st.text_input(
            "Requête de recherche",
            value=st.session_state.get("internship_query", ""),
            placeholder="Ex: Data Scientist Time Series MLOps stage Paris 2026",
            key="search_q"
        )

        if st.button("🔍 Rechercher & Analyser", key="search_btn"):
            if search_query.strip():
                with st.spinner("Recherche sur le web et analyse IA en cours..."):
                    result = call_internship_search(search_query)

                ev = result.get("evaluation", {})
                raw = result.get("raw_results", "")
                report = result.get("report", "")

                # Sauvegarde pour les autres onglets
                st.session_state.last_evaluation = ev
                st.session_state.last_job_description = raw

                if "erreur" in ev:
                    st.error(ev["erreur"])
                else:
                    score = ev.get("score", 0)
                    col_gauge, col_details = st.columns([1, 2])
                    with col_gauge:
                        score_gauge(score)

                    with col_details:
                        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
                        points_forts = ev.get("points_forts", [])
                        if points_forts:
                            card(
                                "Points Forts Matchés",
                                "<br>".join(f"✓ {p}" for p in points_forts),
                                "✅", "green"
                            )
                        points_manquants = ev.get("points_manquants", [])
                        if points_manquants:
                            card(
                                "Compétences Manquantes",
                                "<br>".join(f"→ {p}" for p in points_manquants),
                                "⚠️", "amber"
                            )

                    with st.expander("📋 Résultats bruts DuckDuckGo"):
                        st.text(raw[:2000] + "..." if len(raw) > 2000 else raw)
            else:
                st.warning("Entrez une requête de recherche.")

    # ── TAB 2 : LETTRE ──
    with tab2:
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        st.markdown("<div style='color:#7a9cc0; font-size:13px; margin-bottom:16px;'>Collez la description de l'offre de stage ci-dessous pour générer une lettre personnalisée basée sur votre profil.</div>", unsafe_allow_html=True)

        default_desc = st.session_state.get("last_job_description", "")
        job_desc = st.text_area(
            "Description de l'offre",
            value=default_desc[:500] if default_desc else "",
            placeholder="Collez ici la description complète de l'offre de stage...",
            height=180,
            key="job_desc_letter"
        )

        if st.button("✉️ Générer la Lettre de Motivation", key="gen_letter"):
            if job_desc.strip():
                with st.spinner("Rédaction de la lettre personnalisée..."):
                    letter = call_cover_letter(job_desc)
                st.session_state.cover_letter = letter
                card("Lettre de Motivation", letter.replace("\n", "<br>"), "✉️", "cyan")
                st.download_button(
                    "⬇ Télécharger .txt",
                    data=letter,
                    file_name=f"lettre_motivation_{datetime.now().strftime('%Y%m%d')}.txt",
                    mime="text/plain"
                )
            else:
                st.warning("Collez une description d'offre.")

    # ── TAB 3 : EMAIL RH ──
    with tab3:
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            company = st.text_input("Nom de l'entreprise", placeholder="Ex: Airbus, BNP Paribas, Thales...", key="hr_company")
        with col2:
            job_title = st.text_input("Poste visé", placeholder="Ex: Data Scientist MLOps", key="hr_title")

        if st.button("📧 Générer l'Email RH", key="gen_email"):
            if company.strip() and job_title.strip():
                with st.spinner("Rédaction de l'email de candidature..."):
                    email = call_hr_email(company, job_title)
                st.session_state.hr_email = email
                card("Email RH Personnalisé", email.replace("\n", "<br>"), "📧", "green")
                st.download_button(
                    "⬇ Télécharger .txt",
                    data=email,
                    file_name=f"email_rh_{company.lower().replace(' ','_')}_{datetime.now().strftime('%Y%m%d')}.txt",
                    mime="text/plain"
                )
            else:
                st.warning("Renseignez l'entreprise et le poste visé.")


# ── PAGE : PLANNER ───────────────────────────────────────────
elif module == "planner":
    section_header("Planificateur Académique", "Organisation · Priorisation · Productivité")

    tab1, tab2 = st.tabs(["📅  Plan de Révision", "⚡  Priorisation de Tâches"])

    # ── TAB 1 : PLAN ──
    with tab1:
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        col1, col2 = st.columns([2, 1])
        with col1:
            exam_date = st.date_input(
                "Date de l'examen",
                value=datetime.now(),
                key="exam_date"
            )
        with col2:
            hours_day = st.slider("Heures / jour", 1, 8, 3, key="hours_day")

        topics_input = st.text_area(
            "Thèmes à réviser (un par ligne)",
            placeholder="Machine Learning — Gradient Boosting\nDeep Learning — CNN & Transfer Learning\nNLP — Transformers & BERT\nSéries Temporelles — SARIMAX, LightGBM\nMLOps — MLflow, Docker, FastAPI",
            height=140,
            key="topics_input"
        )

        if st.button("📅 Générer le Plan de Révision", key="gen_plan"):
            if topics_input.strip():
                topics = [t.strip() for t in topics_input.strip().split("\n") if t.strip()]
                with st.spinner(f"Génération du plan ({len(topics)} thèmes, {hours_day}h/jour)..."):
                    plan = call_study_plan(topics, str(exam_date), hours_day)
                st.session_state.study_plan = plan
                card("Plan de Révision Personnalisé", plan.replace("\n", "<br>"), "📅", "cyan")
                st.download_button(
                    "⬇ Télécharger le plan",
                    data=plan,
                    file_name=f"plan_revision_{exam_date}.txt",
                    mime="text/plain"
                )
            else:
                st.warning("Entrez au moins un thème à réviser.")

    # ── TAB 2 : TÂCHES ──
    with tab2:
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        tasks_input = st.text_area(
            "Liste de tâches à prioriser (une par ligne)",
            placeholder="Rendre le rapport de projet MLOps\nRéviser le chapitre LSTM pour l'examen vendredi\nEnvoyer ma candidature à Airbus\nLire la doc LangGraph v2\nPréparer la présentation soutenance\nCoder le pipeline RAG final",
            height=160,
            key="tasks_input"
        )

        if st.button("⚡ Prioriser mes Tâches", key="prio_btn"):
            if tasks_input.strip():
                tasks = [t.strip() for t in tasks_input.strip().split("\n") if t.strip()]
                with st.spinner(f"Analyse de {len(tasks)} tâches en cours..."):
                    result = call_prioritize(tasks)
                card("Matrice de Priorisation — Eisenhower", result.replace("\n", "<br>"), "⚡", "amber")
            else:
                st.warning("Entrez au moins une tâche.")


# ── PAGE : CONFIG ────────────────────────────────────────────
elif module == "config":
    section_header("Configuration Système", "Paramètres · Modèles · Base Vectorielle")

    col1, col2 = st.columns(2)

    with col1:
        card(
            "Stack IA Locale",
            """<strong style='color:#00d4ff'>LLM :</strong> Ollama · Llama 3 (llama3)<br>
            <strong style='color:#00d4ff'>Embeddings :</strong> HuggingFace · all-MiniLM-L6-v2<br>
            <strong style='color:#00d4ff'>Vector DB :</strong> ChromaDB · Persisté sur disque<br>
            <strong style='color:#00d4ff'>Endpoint :</strong> http://localhost:11434""",
            "🖥️", "cyan"
        )

        card(
            "Paramètres RAG",
            """<strong style='color:#00ff88'>Chunk Size :</strong> 1000 tokens<br>
            <strong style='color:#00ff88'>Chunk Overlap :</strong> 150 tokens<br>
            <strong style='color:#00ff88'>Top-K Retrieval :</strong> 4 chunks<br>
            <strong style='color:#00ff88'>Splitter :</strong> RecursiveCharacterTextSplitter""",
            "⚙️", "green"
        )

    with col2:
        card(
            "PDFs Indexés",
            """<code style='color:#00d4ff; font-size:12px;'>BIHAR2026 M32 Machine Learning II - Chapter 4.pdf</code><br><br>
            <code style='color:#00d4ff; font-size:12px;'>BIHAR2026 M33 Deep Learning II - NLP - Chapter 2.pdf</code>""",
            "📚", "amber"
        )

        card(
            "Profil Candidat",
            """<strong style='color:#ffb347'>Nom :</strong> Djakpa Ivan Elie DJALEGA<br>
            <strong style='color:#ffb347'>Formation :</strong> MSc BIHAR · ESTIA<br>
            <strong style='color:#ffb347'>Dispo :</strong> Avril 2026 · 6 mois<br>
            <strong style='color:#ffb347'>Profil :</strong> <code>data/my_profile.txt</code>""",
            "👤", "amber"
        )

    st.markdown("---")
    st.markdown("<div style='color:#3d5a7a; font-family:Space Mono,monospace; font-size:10px; text-transform:uppercase; letter-spacing:0.1em; margin-bottom:16px;'>Actions</div>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🔄 Réindexer les PDFs", use_container_width=True):
            load_vector_db.clear()
            st.session_state.vector_db_ready = False
            with st.spinner("Réindexation en cours..."):
                db, status = load_vector_db()
                if db:
                    st.session_state.vector_db_ready = True
                    st.success("✓ Base vectorielle reconstruite !")
                else:
                    st.error(f"Erreur : {status}")

    with col2:
        if st.button("🧹 Effacer l'Historique", use_container_width=True):
            st.session_state.chat_history = []
            try:
                from app.memory.storage import clear_memory
                clear_memory()
            except Exception:
                pass
            st.success("✓ Historique effacé.")

    with col3:
        if st.button("🩺 Tester Ollama", use_container_width=True):
            try:
                import httpx
                r = httpx.get("http://localhost:11434/api/tags", timeout=5)
                if r.status_code == 200:
                    models = r.json().get("models", [])
                    names = [m["name"] for m in models]
                    st.success(f"✓ Ollama actif · Modèles : {', '.join(names)}")
                else:
                    st.error("Ollama répond mais statut inattendu.")
            except Exception as e:
                st.error(f"Ollama inaccessible : {e}\n\nLancez `ollama serve` dans un terminal.")

    # Commandes de démarrage
    st.markdown("---")
    st.markdown("<div style='color:#3d5a7a; font-family:Space Mono,monospace; font-size:10px; text-transform:uppercase; letter-spacing:0.1em; margin-bottom:12px;'>Commandes de démarrage</div>", unsafe_allow_html=True)
    st.code("""# Terminal 1 — Lancer Ollama
ollama serve

# Terminal 2 — Lancer l'interface Streamlit
cd /media/seagate/Projets_IA/ai_personal_agent
source venv/bin/activate
streamlit run streamlit_app.py

# Optionnel — Vérifier les modèles disponibles
ollama list
ollama pull llama3
""", language="bash")