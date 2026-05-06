"""
╔══════════════════════════════════════════════════════════════╗
║        DIAGNOSTIC MACHINE — AI Personal Agent               ║
║        Analyse GPU / CPU / RAM / Ollama / Stack IA          ║
╚══════════════════════════════════════════════════════════════╝
"""

import subprocess
import sys
import os
import platform

# ── Auto-install des dépendances si manquantes ──────────────────
def install(pkg):
    subprocess.check_call([sys.executable, "-m", "pip", "install", pkg, "-q"])

for pkg in ["psutil", "gputil", "tabulate"]:
    try:
        __import__(pkg.lower().replace("-", "_"))
    except ImportError:
        print(f"  Installation de {pkg}...")
        install(pkg)

import psutil
import tabulate as tabulate_mod
from tabulate import tabulate

# ── Helpers ──────────────────────────────────────────────────────
SEP  = "─" * 62
SEP2 = "═" * 62

def header(title):
    print(f"\n{SEP2}")
    print(f"  {title}")
    print(SEP2)

def section(title):
    print(f"\n  ┌─ {title}")

def row(label, value, note=""):
    note_str = f"  ← {note}" if note else ""
    print(f"  │  {label:<28} {str(value):<18}{note_str}")

def ok(msg):   print(f"  │  ✅  {msg}")
def warn(msg): print(f"  │  ⚠️   {msg}")
def err(msg):  print(f"  │  ❌  {msg}")

def recommend(label, value, note=""):
    print(f"  ▶  {label:<30} {value}  {note}")

# ════════════════════════════════════════════════════════════════
# 1. SYSTÈME
# ════════════════════════════════════════════════════════════════
header("1 · SYSTÈME")
section("OS & Plateforme")
row("OS",         platform.system() + " " + platform.release())
row("Architecture", platform.machine())
row("Python",     sys.version.split()[0])
row("Hostname",   platform.node())

# ════════════════════════════════════════════════════════════════
# 2. CPU
# ════════════════════════════════════════════════════════════════
header("2 · CPU")
section("Processeur")

cpu_name = "Inconnu"
try:
    if platform.system() == "Linux":
        with open("/proc/cpuinfo") as f:
            for line in f:
                if "model name" in line:
                    cpu_name = line.split(":")[1].strip()
                    break
    elif platform.system() == "Windows":
        cpu_name = subprocess.check_output("wmic cpu get name", shell=True).decode().split("\n")[1].strip()
    elif platform.system() == "Darwin":
        cpu_name = subprocess.check_output(["sysctl", "-n", "machdep.cpu.brand_string"]).decode().strip()
except:
    pass

phys_cores = psutil.cpu_count(logical=False)
log_cores  = psutil.cpu_count(logical=True)
freq       = psutil.cpu_freq()
cpu_use    = psutil.cpu_percent(interval=1)

row("Modèle CPU",     cpu_name[:45])
row("Cœurs physiques", phys_cores)
row("Threads logiques", log_cores)
row("Fréquence max",  f"{freq.max:.0f} MHz" if freq else "N/A")
row("Utilisation",    f"{cpu_use}%")

# Score CPU pour LLM
cpu_score = "Faible"
note_cpu  = "Inférence lente sur CPU pur"
if phys_cores >= 16:
    cpu_score = "Très bon"
    note_cpu = "Peut faire tourner des modèles quantisés Q4 ~4B"
elif phys_cores >= 8:
    cpu_score = "Bon"
    note_cpu = "Modèles 7B Q4 acceptables (~2-5 tok/s)"
elif phys_cores >= 4:
    cpu_score = "Moyen"
    note_cpu = "Modèles 3B-7B Q4 lents"

print(f"\n  │  → Score CPU pour LLM : [{cpu_score}] — {note_cpu}")

# ════════════════════════════════════════════════════════════════
# 3. RAM
# ════════════════════════════════════════════════════════════════
header("3 · RAM")
section("Mémoire Système")

ram      = psutil.virtual_memory()
swap     = psutil.swap_memory()
ram_gb   = ram.total / 1024**3
free_gb  = ram.available / 1024**3
used_pct = ram.percent

row("RAM totale",    f"{ram_gb:.1f} GB")
row("RAM disponible", f"{free_gb:.1f} GB")
row("Utilisation",   f"{used_pct}%")
row("Swap total",    f"{swap.total / 1024**3:.1f} GB")

# Recommandation RAM
ram_note = ""
if ram_gb >= 64:
    ram_note = "Excellent — modèles 70B quantisés possibles"
elif ram_gb >= 32:
    ram_note = "Très bien — 13B-34B quantisés confortables"
elif ram_gb >= 16:
    ram_note = "Bien — 7B-13B quantisés OK"
elif ram_gb >= 8:
    ram_note = "Limité — 3B-7B uniquement"
else:
    ram_note = "Insuffisant pour des modèles performants"

if used_pct > 80:
    warn(f"RAM chargée à {used_pct}% — fermez des applications avant l'inférence")
else:
    ok(f"RAM disponible suffisante ({free_gb:.1f} GB libres)")

print(f"  │  → {ram_note}")

# ════════════════════════════════════════════════════════════════
# 4. GPU
# ════════════════════════════════════════════════════════════════
header("4 · GPU (NVIDIA)")

gpu_found    = False
gpu_data     = []
total_vram   = 0

# Méthode 1 : nvidia-smi
try:
    smi_out = subprocess.check_output(
        ["nvidia-smi",
         "--query-gpu=name,memory.total,memory.free,memory.used,temperature.gpu,utilization.gpu,driver_version",
         "--format=csv,noheader,nounits"],
        stderr=subprocess.DEVNULL
    ).decode().strip()

    for i, line in enumerate(smi_out.split("\n")):
        parts = [p.strip() for p in line.split(",")]
        if len(parts) >= 7:
            name, mem_total, mem_free, mem_used, temp, util, driver = parts[:7]
            total_mb  = int(mem_total)
            free_mb   = int(mem_free)
            used_mb   = int(mem_used)
            vram_gb   = total_mb / 1024
            total_vram += vram_gb

            gpu_data.append({
                "id": i, "name": name,
                "vram_gb": vram_gb, "free_mb": free_mb,
                "used_mb": used_mb, "temp": temp, "util": util,
                "driver": driver
            })

            section(f"GPU {i} — {name}")
            row("VRAM totale",   f"{vram_gb:.1f} GB")
            row("VRAM libre",    f"{free_mb / 1024:.1f} GB")
            row("VRAM utilisée", f"{used_mb / 1024:.1f} GB")
            row("Température",   f"{temp}°C")
            row("Utilisation",   f"{util}%")
            row("Driver NVIDIA", driver)
            gpu_found = True

except (subprocess.CalledProcessError, FileNotFoundError):
    pass

# Méthode 2 : GPUtil (fallback)
if not gpu_found:
    try:
        import GPUtil
        gpus = GPUtil.getGPUs()
        for gpu in gpus:
            vram_gb = gpu.memoryTotal / 1024
            total_vram += vram_gb
            section(f"GPU {gpu.id} — {gpu.name}")
            row("VRAM totale",   f"{vram_gb:.1f} GB")
            row("VRAM libre",    f"{gpu.memoryFree / 1024:.1f} GB")
            row("Utilisation",   f"{gpu.load * 100:.0f}%")
            row("Température",   f"{gpu.temperature}°C")
            gpu_found = True
    except:
        pass

# Méthode 3 : AMD / ROCm
if not gpu_found:
    try:
        rocm = subprocess.check_output(["rocm-smi", "--showmeminfo", "vram"], stderr=subprocess.DEVNULL).decode()
        print(f"\n  AMD GPU détecté (ROCm)")
        print(rocm[:300])
        gpu_found = True
    except:
        pass

if not gpu_found:
    warn("Aucun GPU NVIDIA/AMD détecté (ou drivers non installés)")
    warn("L'inférence se fera sur CPU — vitesse réduite")

# ════════════════════════════════════════════════════════════════
# 5. CUDA
# ════════════════════════════════════════════════════════════════
header("5 · CUDA & PyTorch")
section("CUDA")

cuda_available = False
try:
    import torch
    cuda_available = torch.cuda.is_available()
    row("PyTorch version",  torch.__version__)
    row("CUDA disponible",  "✅ OUI" if cuda_available else "❌ NON")
    if cuda_available:
        row("CUDA version",    torch.version.cuda)
        row("Devices CUDA",    torch.cuda.device_count())
        for i in range(torch.cuda.device_count()):
            props = torch.cuda.get_device_properties(i)
            row(f"  GPU {i} name",  props.name)
            row(f"  GPU {i} VRAM",  f"{props.total_memory / 1024**3:.1f} GB")
            row(f"  Compute cap.", f"{props.major}.{props.minor}")
        ok("GPU CUDA prêt pour l'inférence accélérée !")
    else:
        warn("CUDA non disponible — inférence CPU uniquement")
except ImportError:
    warn("PyTorch non installé dans ce venv")
    warn("Installe : pip install torch")

# ════════════════════════════════════════════════════════════════
# 6. OLLAMA
# ════════════════════════════════════════════════════════════════
header("6 · OLLAMA")
section("Service & Modèles")

try:
    import httpx
    r = httpx.get("http://localhost:11434/api/tags", timeout=3)
    if r.status_code == 200:
        ok("Ollama est en cours d'exécution ✅")
        models = r.json().get("models", [])
        if models:
            print(f"\n  Modèles installés ({len(models)}) :")
            rows = []
            for m in models:
                name    = m.get("name", "?")
                size_b  = m.get("size", 0)
                size_gb = f"{size_b / 1024**3:.1f} GB"
                modified = m.get("modified_at", "")[:10]
                rows.append([name, size_gb, modified])
            print(tabulate(rows, headers=["Modèle", "Taille", "Modifié le"],
                           tablefmt="simple", colalign=("left", "right", "left")))
        else:
            warn("Aucun modèle installé. Lance : ollama pull llama3")
    else:
        err("Ollama répond mais statut inattendu")
except Exception as e:
    err(f"Ollama inaccessible — lance 'ollama serve' d'abord")
    err(f"Détail : {e}")

# ════════════════════════════════════════════════════════════════
# 7. DISQUE
# ════════════════════════════════════════════════════════════════
header("7 · STOCKAGE")
section("Espace disque")

for part in psutil.disk_partitions():
    try:
        usage = psutil.disk_usage(part.mountpoint)
        total = usage.total / 1024**3
        free  = usage.free  / 1024**3
        pct   = usage.percent
        if total > 1:  # ignore tiny partitions
            flag = "⚠️ " if pct > 85 else "✅"
            row(part.mountpoint[:28], f"{free:.1f}/{total:.1f} GB libres", f"{flag} {pct}% utilisé")
    except:
        pass

# ════════════════════════════════════════════════════════════════
# 8. RECOMMANDATIONS MODÈLES
# ════════════════════════════════════════════════════════════════
header("8 · RECOMMANDATIONS — MODÈLES OLLAMA")

print("\n  Basé sur ta configuration :\n")

# Calcul du profil
vram = total_vram if gpu_found else 0

if vram >= 24:
    tier = "HIGH_END"
elif vram >= 12:
    tier = "MID_HIGH"
elif vram >= 8:
    tier = "MID"
elif vram >= 6:
    tier = "LOW_MID"
elif ram_gb >= 32:
    tier = "CPU_HIGH"
else:
    tier = "CPU_LOW"

recs = {
    "HIGH_END": [
        ("mistral-nemo",      "12B",  "ollama pull mistral-nemo",       "⭐⭐⭐⭐⭐ Meilleur équilibre qualité/vitesse"),
        ("llama3.1:70b-q4",   "70B",  "ollama pull llama3.1:70b-q4_0",  "⭐⭐⭐⭐⭐ Qualité maximale (lent)"),
        ("deepseek-r1:32b",   "32B",  "ollama pull deepseek-r1:32b",    "⭐⭐⭐⭐⭐ Raisonnement avancé"),
        ("qwen2.5-coder:32b", "32B",  "ollama pull qwen2.5-coder:32b",  "⭐⭐⭐⭐⭐ Meilleur pour le code/JSON"),
    ],
    "MID_HIGH": [
        ("mistral-nemo",      "12B",  "ollama pull mistral-nemo",       "⭐⭐⭐⭐⭐ RECOMMANDÉ — parfait pour toi"),
        ("llama3.1:13b",      "13B",  "ollama pull llama3.1:13b",       "⭐⭐⭐⭐  Bon généraliste"),
        ("deepseek-r1:14b",   "14B",  "ollama pull deepseek-r1:14b",    "⭐⭐⭐⭐⭐ Raisonnement excellent"),
        ("qwen2.5-coder:14b", "14B",  "ollama pull qwen2.5-coder:14b",  "⭐⭐⭐⭐  JSON / code fiable"),
    ],
    "MID": [
        ("mistral:7b-instruct","7B",  "ollama pull mistral:7b-instruct","⭐⭐⭐⭐⭐ RECOMMANDÉ — rapide et précis"),
        ("llama3.1:8b",        "8B",  "ollama pull llama3.1:8b",        "⭐⭐⭐⭐  Bon généraliste"),
        ("deepseek-r1:8b",     "8B",  "ollama pull deepseek-r1:8b",     "⭐⭐⭐⭐  Raisonnement 8B"),
        ("qwen2.5:7b",         "7B",  "ollama pull qwen2.5:7b",         "⭐⭐⭐⭐  JSON structuré"),
    ],
    "LOW_MID": [
        ("mistral:7b-q4",      "7B",  "ollama pull mistral:7b-q4_0",   "⭐⭐⭐⭐  RECOMMANDÉ quantisé Q4"),
        ("llama3.2:3b",        "3B",  "ollama pull llama3.2:3b",        "⭐⭐⭐   Léger et rapide"),
        ("phi3:mini",          "3.8B","ollama pull phi3:mini",           "⭐⭐⭐   Très rapide, bon en code"),
        ("qwen2.5:3b",         "3B",  "ollama pull qwen2.5:3b",         "⭐⭐⭐   Petit mais utile"),
    ],
    "CPU_HIGH": [
        ("mistral:7b-q4",      "7B",  "ollama pull mistral:7b-q4_0",   "⭐⭐⭐   Meilleur choix CPU 32GB"),
        ("llama3.2:3b",        "3B",  "ollama pull llama3.2:3b",        "⭐⭐⭐⭐  Plus rapide sur CPU"),
        ("phi3:mini",          "3.8B","ollama pull phi3:mini",           "⭐⭐⭐⭐  Optimisé CPU"),
    ],
    "CPU_LOW": [
        ("llama3.2:3b",        "3B",  "ollama pull llama3.2:3b",        "⭐⭐⭐   Seul choix viable"),
        ("phi3:mini",          "3.8B","ollama pull phi3:mini",           "⭐⭐⭐   Très léger"),
        ("tinyllama",          "1.1B","ollama pull tinyllama",           "⭐⭐    Ultra-léger (limité)"),
    ],
}

labels = {"HIGH_END": "GPU 24GB+", "MID_HIGH": "GPU 12-16GB", "MID": "GPU 8GB",
          "LOW_MID": "GPU 6GB", "CPU_HIGH": "CPU/RAM 32GB+", "CPU_LOW": "CPU/RAM 16GB"}

print(f"  Profil détecté : [{labels.get(tier, tier)}]")
print(f"  VRAM : {vram:.1f} GB  |  RAM : {ram_gb:.1f} GB\n")

rec_rows = [[r[0], r[1], r[3]] for r in recs[tier]]
print(tabulate(rec_rows, headers=["Modèle", "Taille", "Évaluation"],
               tablefmt="rounded_outline"))

print(f"\n  Commandes d'installation :")
for r in recs[tier]:
    print(f"    {r[2]}")

# ════════════════════════════════════════════════════════════════
# 9. MISE À JOUR CONFIG SUGGÉRÉE
# ════════════════════════════════════════════════════════════════
header("9 · MISE À JOUR app/config.py SUGGÉRÉE")

best_model = recs[tier][0][0]
print(f"""
  Remplace dans app/config.py :

  ┌─────────────────────────────────────────────────┐
  │  class Config:                                  │
  │      LLM_MODEL = "{best_model:<32}" │
  │      OLLAMA_BASE_URL = "http://localhost:11434" │
  └─────────────────────────────────────────────────┘

  Commande rapide :
    ollama pull {best_model}
""")

print(SEP2)
print("  Diagnostic terminé.")
print(SEP2 + "\n")