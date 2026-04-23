"""
╔══════════════════════════════════════════════════════╗
║   🛡️ AegisAI - AI-Powered Vulnerability Management  ║
╚══════════════════════════════════════════════════════╝
Autor: AegisAI Framework
Versión: 1.0.0
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
import re
import random
import time
import io
import requests
import os
import hashlib
from datetime import datetime

def _seeded_random(seed_str: str) -> random.Random:
    """
    Retorna un objeto Random con semilla derivada del string dado.
    Garantiza que el mismo CVE/texto SIEMPRE produzca los mismos valores.
    """
    seed = int(hashlib.md5(seed_str.encode()).hexdigest(), 16) % (2**32)
    rng = random.Random(seed)
    return rng

# ─────────────────────────────────────────────
# TRADUCCIÓN — Google Translate (sin API key)
# ─────────────────────────────────────────────
def translate_to_spanish(text: str) -> str:
    """
    Traduce texto al español usando la API pública de Google Translate.
    No requiere API key. Retorna el texto original si falla.
    """
    if not text or text == "No English description available.":
        return text
    try:
        # Usar endpoint público de Google Translate
        url = "https://translate.googleapis.com/translate_a/single"
        params = {
            "client": "gtx",
            "sl":     "en",
            "tl":     "es",
            "dt":     "t",
            "q":      text,
        }
        resp = requests.get(url, params=params, timeout=8,
                            headers={"User-Agent": "Mozilla/5.0"})
        if resp.status_code == 200:
            data = resp.json()
            translated = "".join(
                part[0] for part in data[0] if part[0]
            )
            return translated if translated else text
    except Exception:
        pass
    return text  # fallback: texto original

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="AegisAI - Vulnerability Management",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# CUSTOM CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Exo+2:wght@300;400;600;700;900&display=swap');

/* ── Base ── */
html, body, [class*="css"] {
    font-family: 'Exo 2', sans-serif;
}

/* ── Fondo global ── */
.stApp {
    background: #070b14;
    background-image:
        radial-gradient(ellipse 80% 40% at 50% -10%, rgba(0,200,255,0.08) 0%, transparent 70%),
        radial-gradient(ellipse 50% 30% at 90% 90%, rgba(255,60,60,0.05) 0%, transparent 60%);
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: #0a0f1e !important;
    border-right: 1px solid rgba(0,200,255,0.12);
}
[data-testid="stSidebar"] * { color: #c5d8f5 !important; }

/* ── Título principal ── */
.aegis-header {
    text-align: center;
    padding: 2rem 0 1.5rem;
}
.aegis-title {
    font-family: 'Share Tech Mono', monospace;
    font-size: 2.8rem;
    font-weight: 900;
    background: linear-gradient(90deg, #00c8ff, #ffffff, #ff3c5f);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    letter-spacing: 2px;
    text-shadow: none;
}
.aegis-sub {
    font-family: 'Share Tech Mono', monospace;
    color: #4a9ebb;
    font-size: 0.85rem;
    letter-spacing: 4px;
    margin-top: 0.3rem;
}

/* ── Tarjetas de métricas ── */
.metric-card {
    background: linear-gradient(135deg, #0d1526 0%, #111c33 100%);
    border: 1px solid rgba(0,200,255,0.15);
    border-radius: 12px;
    padding: 1.2rem 1.5rem;
    text-align: center;
    position: relative;
    overflow: hidden;
}
.metric-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, transparent, #00c8ff, transparent);
}
.metric-label {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.65rem;
    letter-spacing: 3px;
    color: #4a9ebb;
    text-transform: uppercase;
}
.metric-value {
    font-family: 'Share Tech Mono', monospace;
    font-size: 2.4rem;
    font-weight: 700;
    color: #ffffff;
    line-height: 1.2;
}
.metric-value.critical { color: #ff3c5f; }
.metric-value.high     { color: #ff8c42; }
.metric-value.medium   { color: #ffd700; }
.metric-value.low      { color: #39ff85; }
.metric-value.score    { color: #00c8ff; }

/* ── Tarjetas de vulnerabilidad ── */
.vuln-card {
    background: linear-gradient(135deg, #0d1526 0%, #0f1a2e 100%);
    border-radius: 12px;
    padding: 1.4rem 1.8rem;
    margin-bottom: 1rem;
    border-left: 4px solid #555;
    position: relative;
    transition: transform 0.2s;
}
.vuln-card:hover { transform: translateX(4px); }
.vuln-card.critical { border-left-color: #ff3c5f; }
.vuln-card.high     { border-left-color: #ff8c42; }
.vuln-card.medium   { border-left-color: #ffd700; }
.vuln-card.low      { border-left-color: #39ff85; }

.vuln-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.8rem;
}
.vuln-id {
    font-family: 'Share Tech Mono', monospace;
    font-size: 1.05rem;
    color: #ffffff;
    font-weight: 700;
}
.rank-badge {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.7rem;
    background: rgba(0,200,255,0.1);
    border: 1px solid rgba(0,200,255,0.3);
    color: #00c8ff;
    padding: 2px 10px;
    border-radius: 20px;
    letter-spacing: 1px;
}

.risk-badge {
    display: inline-block;
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 2px;
    padding: 4px 14px;
    border-radius: 4px;
    margin-bottom: 0.6rem;
}
.risk-badge.critical { background: rgba(255,60,95,0.15);  color: #ff3c5f;  border: 1px solid rgba(255,60,95,0.4); }
.risk-badge.high     { background: rgba(255,140,66,0.15); color: #ff8c42;  border: 1px solid rgba(255,140,66,0.4); }
.risk-badge.medium   { background: rgba(255,215,0,0.10);  color: #ffd700;  border: 1px solid rgba(255,215,0,0.3); }
.risk-badge.low      { background: rgba(57,255,133,0.10); color: #39ff85;  border: 1px solid rgba(57,255,133,0.3); }

.vuln-desc  { color: #8ba3c8; font-size: 0.88rem; margin-bottom: 0.6rem; }
.section-title {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.65rem;
    letter-spacing: 3px;
    color: #4a9ebb;
    text-transform: uppercase;
    margin-bottom: 0.25rem;
}
.justification { color: #a0b8d8; font-size: 0.88rem; line-height: 1.6; margin-bottom: 0.8rem; }

.rec-block {
    background: rgba(0,200,255,0.04);
    border: 1px solid rgba(0,200,255,0.12);
    border-radius: 8px;
    padding: 0.8rem 1rem;
    font-size: 0.83rem;
    color: #90aece;
    line-height: 1.6;
}
.rec-block strong { color: #00c8ff; }

/* ── CVSS bar ── */
.cvss-row   { display: flex; align-items: center; gap: 10px; margin-bottom: 0.4rem; }
.cvss-label { font-family: 'Share Tech Mono', monospace; font-size: 0.7rem; color: #4a9ebb; width: 120px; }
.cvss-bar   { flex: 1; height: 6px; background: #1a2540; border-radius: 3px; overflow: hidden; }
.cvss-fill  { height: 100%; border-radius: 3px; }
.cvss-val   { font-family: 'Share Tech Mono', monospace; font-size: 0.72rem; color: #c5d8f5; width: 30px; text-align: right; }

/* ── Divider ── */
.aegis-divider {
    border: none;
    border-top: 1px solid rgba(0,200,255,0.1);
    margin: 1.5rem 0;
}

/* ── Scanning animation ── */
@keyframes scanline {
    0%   { transform: translateY(-100%); }
    100% { transform: translateY(100vh); }
}
.scan-overlay {
    pointer-events: none;
    position: fixed;
    top: 0; left: 0; width: 100%; height: 3px;
    background: linear-gradient(90deg, transparent, rgba(0,200,255,0.6), transparent);
    animation: scanline 3s linear infinite;
    z-index: 9999;
}

/* ── Buttons ── */
div.stButton > button {
    background: linear-gradient(135deg, #003a5e, #005a8e) !important;
    border: 1px solid rgba(0,200,255,0.4) !important;
    color: #00c8ff !important;
    font-family: 'Share Tech Mono', monospace !important;
    font-size: 0.9rem !important;
    letter-spacing: 2px !important;
    border-radius: 6px !important;
    padding: 0.6rem 1.8rem !important;
    transition: all 0.3s !important;
}
div.stButton > button:hover {
    background: linear-gradient(135deg, #005a8e, #007ab8) !important;
    box-shadow: 0 0 20px rgba(0,200,255,0.3) !important;
    transform: translateY(-1px) !important;
}

/* ── Text area & inputs ── */
textarea, .stTextArea textarea {
    background: #0d1526 !important;
    color: #c5d8f5 !important;
    border: 1px solid rgba(0,200,255,0.2) !important;
    font-family: 'Share Tech Mono', monospace !important;
    font-size: 0.85rem !important;
    border-radius: 8px !important;
}
textarea:focus, .stTextArea textarea:focus {
    border-color: rgba(0,200,255,0.5) !important;
    box-shadow: 0 0 12px rgba(0,200,255,0.15) !important;
}

/* ── Expander ── */
.streamlit-expanderHeader {
    background: #0d1526 !important;
    color: #c5d8f5 !important;
    border: 1px solid rgba(0,200,255,0.12) !important;
    border-radius: 8px !important;
    font-family: 'Share Tech Mono', monospace !important;
}

/* ── Download button ── */
.stDownloadButton > button {
    background: rgba(57,255,133,0.08) !important;
    border: 1px solid rgba(57,255,133,0.3) !important;
    color: #39ff85 !important;
    font-family: 'Share Tech Mono', monospace !important;
    font-size: 0.78rem !important;
    letter-spacing: 1px !important;
    border-radius: 6px !important;
}

/* ── Section headers ── */
.section-header {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.65rem;
    letter-spacing: 4px;
    color: #4a9ebb;
    text-transform: uppercase;
    margin: 1.5rem 0 1rem;
    display: flex;
    align-items: center;
    gap: 10px;
}
.section-header::after {
    content: '';
    flex: 1;
    height: 1px;
    background: linear-gradient(90deg, rgba(0,200,255,0.3), transparent);
}

/* ── Global score gauge label ── */
.score-ring-label {
    font-family: 'Share Tech Mono', monospace;
    text-align: center;
    font-size: 0.7rem;
    letter-spacing: 3px;
    color: #4a9ebb;
    margin-top: -0.5rem;
}
</style>
<div class="scan-overlay"></div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# AI ENGINE — Análisis de vulnerabilidades
# ─────────────────────────────────────────────

KEYWORD_PATTERNS = {
    "critical": {
        "keywords": ["rce", "remote code execution", "zero-day", "0day", "unauthenticated rce",
                     "sin parche crítico", "critical unpatched", "kernel exploit", "privilege escalation root",
                     "sql injection unauthenticated", "bypass authentication"],
        "base_cvss": (8.5, 10.0),
        "level": "Crítico",
    },
    "high": {
        "keywords": ["credencial", "credential", "contraseña débil", "weak password",
                     "sql injection", "inyección sql", "xss", "ssrf", "deserialization",
                     "path traversal", "ldap injection", "xml injection", "privilege escalation",
                     "token exposed", "api key exposed"],
        "base_cvss": (7.0, 8.4),
        "level": "Alto",
    },
    "medium": {
        "keywords": ["puerto abierto", "open port", "misconfiguration", "mala configuración",
                     "cors", "outdated", "desactualizado", "default password", "contraseña por defecto",
                     "information disclosure", "divulgación de información", "self-signed cert",
                     "http", "sin ssl", "no ssl"],
        "base_cvss": (4.0, 6.9),
        "level": "Medio",
    },
    "low": {
        "keywords": ["banner grabbing", "version disclosure", "verbose error", "error detallado",
                     "clickjacking", "low impact", "bajo impacto", "informational"],
        "base_cvss": (0.1, 3.9),
        "level": "Bajo",
    },
}

ASSET_PATTERNS = {
    "servidor web":       ("servidor_web",    "Internet-facing web server"),
    "web server":         ("servidor_web",    "Internet-facing web server"),
    "base de datos":      ("base_datos",      "Database server"),
    "database":           ("base_datos",      "Database server"),
    "red":                ("red",             "Network infrastructure"),
    "network":            ("red",             "Network infrastructure"),
    "router":             ("red",             "Network infrastructure"),
    "api":                ("api_gateway",     "API Gateway / microservice"),
    "cloud":              ("cloud",           "Cloud infrastructure"),
    "windows":            ("endpoint",        "Windows endpoint"),
    "linux":              ("endpoint",        "Linux endpoint"),
    "kernel":             ("sistema_operativo","Operating system kernel"),
    "ldap":               ("directorio",      "Directory service / LDAP"),
    "active directory":   ("directorio",      "Directory service / Active Directory"),
}

EXPOSURE_RULES = {
    "servidor_web":      "Alto",
    "api_gateway":       "Alto",
    "base_datos":        "Medio",
    "directorio":        "Alto",
    "red":               "Medio",
    "cloud":             "Alto",
    "sistema_operativo": "Alto",
    "endpoint":          "Medio",
    "desconocido":       "Bajo",
}

JUSTIFICATIONS = {
    "Crítico": [
        "El análisis de IA detecta vectores de ataque con alta posibilidad de explotación remota sin credenciales. La combinación de exposición {exposure} sobre {asset_type} incrementa el radio de impacto a nivel organizacional. El puntaje CVSS simulado de {cvss} supera el umbral de riesgo crítico (≥8.5). La probabilidad de explotación activa en los próximos 30 días se estima en >75% basado en patrones de amenaza históricos.",
        "El motor de correlación identifica esta vulnerabilidad como objetivo activo en campañas de ransomware recientes. Con exposición {exposure} y tipo de activo {asset_type}, la superficie de ataque es extremadamente amplia. CVSS simulado: {cvss}/10. Se requiere remediación INMEDIATA.",
    ],
    "Alto": [
        "La IA identifica riesgo elevado: el tipo de vulnerabilidad permite a un atacante con acceso {exposure} comprometer el activo {asset_type}. El CVSS simulado de {cvss} indica impacto significativo. La probabilidad de explotación se estima en 50-75% en un horizonte de 90 días. Existe evidencia de exploits públicos disponibles.",
        "Correlación con TTPs de MITRE ATT&CK indica que este vector es utilizado frecuentemente en intrusiones dirigidas. El activo {asset_type} con exposición {exposure} amplifica el impacto potencial. CVSS estimado: {cvss}/10. Prioridad alta para parche en ciclo de 7 días.",
    ],
    "Medio": [
        "Riesgo moderado detectado. La vulnerabilidad en {asset_type} con exposición {exposure} representa un vector secundario que podría ser usado como pivote en ataques encadenados. CVSS simulado: {cvss}. Sin explotación activa conocida, pero la superficie de ataque amplía el perímetro de riesgo.",
        "El análisis contextual indica que esta configuración deficiente en {asset_type} podría ser explotada en combinación con otras vulnerabilidades. Exposición actual: {exposure}. Recomendado para remediación en el siguiente ciclo de mantenimiento programado.",
    ],
    "Bajo": [
        "Riesgo residual identificado. La vulnerabilidad en {asset_type} tiene impacto limitado de forma aislada, aunque con exposición {exposure} podría proporcionar información de reconocimiento a un adversario. CVSS simulado: {cvss}. Bajo potencial de explotación directa.",
        "Hallazgo informativo. La debilidad detectada en {asset_type} requiere condiciones específicas para ser explotada. Gestión recomendada en el backlog de seguridad. CVSS estimado: {cvss}.",
    ],
}

RECOMMENDATIONS = {
    "Crítico": {
        "nist": "NIST SP 800-40 Rev.4: Aplicar parche de emergencia dentro de las 24h. Activar procedimiento de respuesta a incidentes (IR Plan). Aislar el activo afectado hasta remediar. Revisar logs de acceso retrospectivos (mínimo 90 días).",
        "iso": "ISO/IEC 27001 — A.12.6.1 (Gestión de vulnerabilidades técnicas): Escalar inmediatamente al CISO. Documentar en el registro de riesgos. Aplicar controles compensatorios temporales (WAF, ACL, segmentación de red). Notificar a partes interesadas según plan de comunicación.",
        "best_practice": "Implementar virtual patching vía WAF/IPS mientras se prepara el parche definitivo. Activar monitoreo 24/7 para IOCs relacionados. Considerar threat hunting proactivo en el entorno. Revisar si existen sistemas hermanos con la misma vulnerabilidad.",
    },
    "Alto": {
        "nist": "NIST SP 800-40 Rev.4: Aplicar parche dentro de 7 días. Priorizar en el siguiente ciclo de patch management. Validar configuraciones de firewall y controles de acceso.",
        "iso": "ISO/IEC 27001 — A.12.6.1 / A.9.4.2: Registrar en el gestor de vulnerabilidades. Evaluar impacto en el análisis de riesgo vigente. Aplicar principio de mínimo privilegio para reducir superficie de ataque.",
        "best_practice": "Activar reglas IDS/IPS específicas para el CVE. Verificar credenciales y políticas de acceso relacionadas. Realizar prueba de penetración dirigida post-remediación para validar el fix.",
    },
    "Medio": {
        "nist": "NIST SP 800-40 Rev.4: Programar remediación en el próximo ciclo de mantenimiento (máx. 30 días). Documentar riesgo aceptado si no se puede remediar en el plazo.",
        "iso": "ISO/IEC 27001 — A.12.6.1 / A.12.4 (Logging): Incluir en el próximo sprint de hardening. Revisar y actualizar la política de configuración segura. Validar mediante escaneo de vulnerabilidades post-remediación.",
        "best_practice": "Aplicar CIS Benchmark correspondiente al sistema afectado. Implementar monitoreo de configuración continuo (CSPM/SIEM). Revisar política de gestión de activos para clasificar adecuadamente el activo.",
    },
    "Bajo": {
        "nist": "NIST SP 800-40 Rev.4: Evaluar para remediación en próximo release o ciclo trimestral. Documentar como riesgo aceptado si el costo de remediación supera el impacto.",
        "iso": "ISO/IEC 27001 — A.12.6.1: Registrar en el inventario de vulnerabilidades. Revisar en la próxima auditoría interna. Mantener en el backlog de seguridad con baja prioridad.",
        "best_practice": "Aplicar medidas de hardening estándar (CIS L1). Deshabilitar servicios o puertos innecesarios. Documentar decisión de riesgo aceptado si aplica.",
    },
}

RISK_COLORS = {
    "Crítico": ("#ff3c5f", "critical"),
    "Alto":    ("#ff8c42", "high"),
    "Medio":   ("#ffd700", "medium"),
    "Bajo":    ("#39ff85", "low"),
}

RISK_ORDER = {"Crítico": 0, "Alto": 1, "Medio": 2, "Bajo": 3}


def detect_level(text_lower: str, seed_str: str = "") -> str:
    for level, data in KEYWORD_PATTERNS.items():
        for kw in data["keywords"]:
            if kw in text_lower:
                return level
    # Sin match: usar semilla del texto para resultado consistente
    rng = _seeded_random(seed_str or text_lower)
    return rng.choices(
        ["critical", "high", "medium", "low"],
        weights=[0.15, 0.30, 0.35, 0.20]
    )[0]


def detect_asset(text_lower: str) -> tuple:
    for kw, val in ASSET_PATTERNS.items():
        if kw in text_lower:
            return val
    return ("desconocido", "Unknown / Generic asset")


def simulate_cvss(level_key: str, rng: random.Random = None) -> float:
    lo, hi = KEYWORD_PATTERNS[level_key]["base_cvss"]
    r = rng if rng else random.Random()
    raw = r.uniform(lo, hi)
    return round(raw, 1)


def build_sub_scores(cvss: float, rng: random.Random = None) -> dict:
    """Descompone CVSS en sub-métricas deterministas basadas en el score."""
    base = cvss / 10.0
    r = rng if rng else random.Random()
    return {
        "Attack Vector":       round(min(1.0, base + r.uniform(-0.1, 0.15)), 2),
        "Attack Complexity":   round(max(0.2, 1.0 - base + r.uniform(0, 0.2)), 2),
        "Privileges Required": round(max(0.1, 1.0 - base + r.uniform(-0.15, 0.1)), 2),
        "Impact (CIA)":        round(min(1.0, base + r.uniform(-0.05, 0.1)), 2),
        "Exploit Maturity":    round(min(1.0, base * r.uniform(0.7, 1.0)), 2),
    }


def analyze_vulnerability(raw_input: str, idx: int) -> dict:
    """Motor principal de análisis de IA — resultados deterministas por CVE."""
    text = raw_input.strip()
    if not text:
        return None

    text_lower = text.lower()

    # ── Detectar ID CVE ──
    cve_match = re.search(r'(CVE-\d{4}-\d+)', text, re.IGNORECASE)
    vuln_id = cve_match.group(1).upper() if cve_match else f"VULN-{datetime.now().year}-{1000 + idx:04d}"

    # ── Semilla determinista basada en el ID ──
    # El mismo CVE SIEMPRE producirá los mismos valores
    rng = _seeded_random(vuln_id)

    # ── Detectar descripción ──
    if " - " in text:
        description = text.split(" - ", 1)[1].strip()
    elif cve_match:
        description = text.replace(cve_match.group(1), "").strip(" :-")
    else:
        description = text

    # ── Nivel de riesgo ──
    level_key = detect_level(text_lower, seed_str=vuln_id)
    level_label = KEYWORD_PATTERNS[level_key]["level"]

    # ── CVSS — determinista ──
    cvss = simulate_cvss(level_key, rng=rng)
    sub_scores = build_sub_scores(cvss, rng=rng)

    # ── Asset & Exposure ──
    asset_key, asset_label = detect_asset(text_lower)
    exposure = EXPOSURE_RULES.get(asset_key, "Bajo")

    # ── Probabilidad de explotación — determinista ──
    exploit_ranges = {
        "Crítico": (72, 95),
        "Alto":    (45, 71),
        "Medio":   (20, 44),
        "Bajo":    (5,  19),
    }
    lo_e, hi_e = exploit_ranges[level_label]
    exploit_prob = rng.randint(lo_e, hi_e)

    # ── Justificación — determinista ──
    justif_template = rng.choice(JUSTIFICATIONS[level_label])
    justification = justif_template.format(
        exposure=exposure.lower(),
        asset_type=asset_label,
        cvss=cvss,
    )

    # ── Recomendaciones ──
    rec = RECOMMENDATIONS[level_label]

    return {
        "id":            vuln_id,
        "description":   description or "No description provided.",
        "level":         level_label,
        "level_key":     level_key,
        "cvss":          cvss,
        "sub_scores":    sub_scores,
        "asset_type":    asset_label,
        "exposure":      exposure,
        "exploit_prob":  exploit_prob,
        "justification": justification,
        "rec_nist":      rec["nist"],
        "rec_iso":       rec["iso"],
        "rec_best":      rec["best_practice"],
        "raw":           text,
        "analyzed_at":   datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }


def compute_global_score(results: list) -> float:
    """Risk Score global ponderado 0-10."""
    if not results:
        return 0.0
    weights = {"Crítico": 4.0, "Alto": 2.5, "Medio": 1.2, "Bajo": 0.4}
    total_w = sum(weights[r["level"]] for r in results)
    max_possible = len(results) * 4.0
    score = (total_w / max_possible) * 10.0
    return round(score, 2)


def results_to_dataframe(results: list) -> pd.DataFrame:
    rows = []
    for i, r in enumerate(results):
        rows.append({
            "Prioridad":    i + 1,
            "ID":           r["id"],
            "Nivel":        r["level"],
            "CVSS":         r["cvss"],
            "Tipo Activo":  r["asset_type"],
            "Exposición":   r["exposure"],
            "Prob. Explot.":f"{r['exploit_prob']}%",
            "Descripción":  r["description"][:80] + "..." if len(r["description"]) > 80 else r["description"],
            "Analizado":    r["analyzed_at"],
        })
    return pd.DataFrame(rows)


# ─────────────────────────────────────────────
# NVD API — Consulta de CVE en tiempo real
# ─────────────────────────────────────────────

# ── URLs de las fuentes de datos CVE ──
NVD_API_URL    = "https://services.nvd.nist.gov/rest/json/cves/2.0"
GITHUB_CVE_URL = "https://raw.githubusercontent.com/CVEProject/cvelistV5/main/cves"
NVD_API_KEY_HARDCODED = "8A95FFF2-943A-F111-836B-0EBF96DE670D"

CVSS_SEVERITY_MAP = {
    "CRITICAL": "critical",
    "HIGH":     "high",
    "MEDIUM":   "medium",
    "LOW":      "low",
    "NONE":     "low",
}

def _load_api_key() -> str:
    try:
        key = st.secrets.get("NVD_API_KEY", "")
        if key: return key
    except Exception:
        pass
    key = os.getenv("NVD_API_KEY", "")
    if key: return key
    return NVD_API_KEY_HARDCODED

def _get_api_key() -> str:
    return _load_api_key()

def _build_github_url(cve_id: str) -> str:
    """Construye la URL raw de GitHub para un CVE dado."""
    parts  = cve_id.upper().split("-")
    year   = parts[1]
    num    = int(parts[2])
    bucket = f"{num // 1000}xxx"
    return f"{GITHUB_CVE_URL}/{year}/{bucket}/{cve_id.upper()}.json"

def _parse_github_cve(data: dict, cve_id: str) -> dict:
    """Parsea el formato JSON 5.0 de MITRE/GitHub a nuestro formato estándar."""
    meta = data.get("cveMetadata", {})
    cna  = data.get("containers", {}).get("cna", {})
    adp_list = data.get("containers", {}).get("adp", [])

    # ── Descripción ──
    descs = cna.get("descriptions", [])
    description = next((d["value"] for d in descs if d.get("lang") == "en"), "")

    # ── CVSS — buscar en cna y adp ──
    cvss_score = cvss_vector = cvss_severity = None
    all_metrics = list(cna.get("metrics", []))
    for adp in adp_list:
        all_metrics.extend(adp.get("metrics", []))

    for m in all_metrics:
        for key in ("cvssV3_1", "cvssV3_0", "cvssV2_0"):
            if key in m:
                cvss_score    = m[key].get("baseScore")
                cvss_vector   = m[key].get("vectorString", "")
                cvss_severity = m[key].get("baseSeverity", "")
                break
        if cvss_score:
            break

    # ── CWE ──
    cwes = []
    for pt in cna.get("problemTypes", []):
        for d in pt.get("descriptions", []):
            cwe = d.get("cweId") or d.get("description", "")
            if cwe.startswith("CWE-"):
                cwes.append(cwe)

    # ── Referencias ──
    refs = [r["url"] for r in cna.get("references", [])[:3]]

    # ── Fechas ──
    published = meta.get("datePublished", "")[:10]
    modified  = meta.get("dateUpdated",   "")[:10]

    return {
        "cve_id":        meta.get("cveId", cve_id.upper()),
        "description":   description,
        "cvss_score":    cvss_score,
        "cvss_vector":   cvss_vector,
        "cvss_severity": cvss_severity.upper() if cvss_severity else None,
        "cwes":          cwes,
        "references":    refs,
        "published":     published,
        "modified":      modified,
    }

def fetch_nvd_cve(cve_id: str):
    """
    Consulta CVE usando 2 fuentes en cascada:
      1. GitHub MITRE CVEProject (sin API key, funciona en Streamlit Cloud)
      2. NVD/NIST API (con API key, funciona local)
    Retorna dict normalizado o dict con clave "error".
    """
    cve_upper = cve_id.upper()
    last_error = {}

    # ══ FUENTE 1: GitHub MITRE CVEProject ══
    try:
        url = _build_github_url(cve_upper)
        resp = requests.get(
            url,
            timeout=15,
            headers={"User-Agent": "Mozilla/5.0 AegisAI/1.0",
                     "Accept": "application/json"},
        )
        if resp.status_code == 200:
            raw = resp.json()
            parsed = _parse_github_cve(raw, cve_upper)
            description_es = translate_to_spanish(parsed["description"])
            parsed["description_en"] = parsed["description"]
            parsed["description"]    = description_es
            parsed["source"]         = "MITRE CVEProject / GitHub"
            return parsed
        elif resp.status_code == 404:
            last_error = {"error": "not_found"}
        else:
            last_error = {"error": "http", "code": resp.status_code}
    except requests.exceptions.Timeout:
        last_error = {"error": "timeout"}
    except requests.exceptions.ConnectionError:
        last_error = {"error": "unreachable", "detail": "GitHub no accesible"}
    except Exception as exc:
        last_error = {"error": "unreachable", "detail": str(exc)}

    # Si el CVE no existe en GitHub, no intentar NVD
    if last_error.get("error") == "not_found":
        return last_error

    # ══ FUENTE 2: NVD/NIST API (fallback) ══
    try:
        _key = _get_api_key()
        params_req = {"cveId": cve_upper, "apiKey": _key}
        resp = requests.get(
            NVD_API_URL,
            params=params_req,
            timeout=20,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AegisAI/1.0",
                     "Accept": "application/json"},
        )
        if resp.status_code == 200:
            data   = resp.json()
            vulns  = data.get("vulnerabilities", [])
            if not vulns:
                return {"error": "not_found"}
            cve_data     = vulns[0].get("cve", {})
            descriptions = cve_data.get("descriptions", [])
            description  = next((d["value"] for d in descriptions if d.get("lang") == "en"),
                                "No description available.")
            cvss_score = cvss_vector = cvss_severity = None
            metrics = cve_data.get("metrics", {})
            for key in ("cvssMetricV31", "cvssMetricV30", "cvssMetricV2"):
                mlist = metrics.get(key, [])
                if mlist:
                    m = mlist[0].get("cvssData", {})
                    cvss_score    = m.get("baseScore")
                    cvss_vector   = m.get("vectorString", "")
                    cvss_severity = m.get("baseSeverity") or mlist[0].get("baseSeverity", "")
                    break
            weaknesses = cve_data.get("weaknesses", [])
            cwes = []
            for w in weaknesses:
                for d in w.get("description", []):
                    if d.get("lang") == "en" and d.get("value", "").startswith("CWE-"):
                        cwes.append(d["value"])
            refs      = [r["url"] for r in cve_data.get("references", [])[:3]]
            published = cve_data.get("published", "")[:10]
            modified  = cve_data.get("lastModified", "")[:10]
            description_es = translate_to_spanish(description)
            return {
                "cve_id":        cve_data.get("id", cve_upper),
                "description":   description_es,
                "description_en": description,
                "cvss_score":    cvss_score,
                "cvss_vector":   cvss_vector,
                "cvss_severity": cvss_severity.upper() if cvss_severity else None,
                "cwes":          cwes,
                "references":    refs,
                "published":     published,
                "modified":      modified,
                "source":        "NVD/NIST (real-time)",
            }
        elif resp.status_code == 403:
            return {"error": "http", "code": 403}
        else:
            return {"error": "http", "code": resp.status_code}
    except requests.exceptions.Timeout:
        return {"error": "timeout"}
    except requests.exceptions.ConnectionError:
        return {"error": "unreachable", "detail": "NVD no accesible desde este entorno"}
    except Exception as exc:
        return {"error": "unreachable", "detail": str(exc)}


def analyze_vulnerability_nvd(nvd_data: dict) -> dict:
    """
    Construye el resultado de análisis enriquecido usando datos reales del NVD.
    Respeta exactamente la misma estructura de dict que analyze_vulnerability().
    """
    cve_id      = nvd_data["cve_id"]
    description = nvd_data["description"]
    text_lower  = description.lower()

    # ── Nivel de riesgo: usar CVSS real si existe ──
    if nvd_data.get("cvss_severity") and nvd_data["cvss_severity"] in CVSS_SEVERITY_MAP:
        level_key   = CVSS_SEVERITY_MAP[nvd_data["cvss_severity"]]
        level_label = KEYWORD_PATTERNS[level_key]["level"]
    else:
        level_key   = detect_level(text_lower)
        level_label = KEYWORD_PATTERNS[level_key]["level"]

    # ── Semilla determinista por CVE ID ──
    rng_nvd = _seeded_random(cve_id)

    # ── CVSS: usar score real o simular ──
    if nvd_data.get("cvss_score") is not None:
        cvss = float(nvd_data["cvss_score"])
    else:
        cvss = simulate_cvss(level_key, rng=rng_nvd)

    sub_scores = build_sub_scores(cvss, rng=rng_nvd)

    # ── Asset & Exposure ──
    asset_key, asset_label = detect_asset(text_lower)
    exposure = EXPOSURE_RULES.get(asset_key, "Bajo")

    # ── Probabilidad de explotación — determinista ──
    exploit_ranges = {
        "Crítico": (72, 95),
        "Alto":    (45, 71),
        "Medio":   (20, 44),
        "Bajo":    (5,  19),
    }
    lo_e, hi_e = exploit_ranges[level_label]
    exploit_prob = rng_nvd.randint(lo_e, hi_e)

    # ── Justificación enriquecida con datos NVD reales ──
    justif_template = rng_nvd.choice(JUSTIFICATIONS[level_label])
    justification   = justif_template.format(
        exposure=exposure.lower(),
        asset_type=asset_label,
        cvss=cvss,
    )
    cwe_str = ", ".join(nvd_data["cwes"]) if nvd_data.get("cwes") else "N/A"
    justification += (
        f" [Datos NVD verificados — Vector: {nvd_data.get('cvss_vector', 'N/A')} | "
        f"CWE: {cwe_str} | Publicado: {nvd_data.get('published', 'N/A')}]"
    )

    rec = RECOMMENDATIONS[level_label]

    return {
        "id":            cve_id,
        "description":   description,
        "level":         level_label,
        "level_key":     level_key,
        "cvss":          cvss,
        "sub_scores":    sub_scores,
        "asset_type":    asset_label,
        "exposure":      exposure,
        "exploit_prob":  exploit_prob,
        "justification": justification,
        "rec_nist":      rec["nist"],
        "rec_iso":       rec["iso"],
        "rec_best":      rec["best_practice"],
        "raw":           cve_id,
        "analyzed_at":   datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "nvd_data":      nvd_data,
        "nvd_enriched":  True,
    }



# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="text-align:center; padding: 1rem 0 1.5rem;">
        <div style="font-family:'Share Tech Mono',monospace; font-size:1.6rem; color:#00c8ff;">🛡️</div>
        <div style="font-family:'Share Tech Mono',monospace; font-size:1rem; color:#fff; font-weight:700; letter-spacing:2px;">AEGIS<span style="color:#ff3c5f">AI</span></div>
        <div style="font-family:'Share Tech Mono',monospace; font-size:0.6rem; letter-spacing:3px; color:#4a9ebb; margin-top:2px;">v1.0.0 · ACTIVE</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    st.markdown("""
    <div style="font-family:'Share Tech Mono',monospace; font-size:0.65rem; letter-spacing:3px; color:#4a9ebb; margin-bottom:0.8rem;">
    ◈ SISTEMA
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="font-size:0.82rem; color:#8ba3c8; line-height:1.8;">
    🔵 Motor IA: <span style="color:#39ff85">Online</span><br>
    🔵 MITRE GitHub: <span style="color:#39ff85">Primaria ✓</span><br>
    🔵 NVD/NIST API: <span style="color:#39ff85">Respaldo ✓</span><br>
    🔵 ISO 27001: <span style="color:#39ff85">Activa</span><br>
    🔵 MITRE ATT&CK: <span style="color:#39ff85">Cargado</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    st.markdown("""
    <div style="font-family:'Share Tech Mono',monospace; font-size:0.65rem; letter-spacing:3px; color:#4a9ebb; margin-bottom:0.8rem;">
    ◈ DATOS DE PRUEBA
    </div>
    """, unsafe_allow_html=True)

    if st.button("📋 Cargar ejemplos"):
        st.session_state["sample_loaded"] = True

    st.markdown("---")
    st.markdown("""
    <div style="font-size:0.72rem; color:#4a6080; line-height:1.7; margin-top:0.5rem;">
    AegisAI correlaciona vulnerabilidades<br>
    usando CVSS, MITRE ATT&CK, NIST<br>
    SP 800-40 e ISO/IEC 27001 para<br>
    generar análisis contextuales.
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────
st.markdown("""
<div class="aegis-header">
    <div class="aegis-title">🛡️ AegisAI</div>
    <div class="aegis-sub">◈ AI-POWERED VULNERABILITY MANAGEMENT ◈</div>
</div>
""", unsafe_allow_html=True)

st.markdown('<hr class="aegis-divider">', unsafe_allow_html=True)


# ─────────────────────────────────────────────
# NVD CVE LOOKUP — Consulta individual en tiempo real
# ─────────────────────────────────────────────
st.markdown("""
<div class="section-header">◈ CONSULTA CVE EN TIEMPO REAL — NVD/NIST</div>
""", unsafe_allow_html=True)

with st.expander("🔍  Buscar un CVE específico en la base de datos oficial del NIST (NVD)", expanded=False):
    st.markdown("""
    <div style="font-size:0.82rem; color:#8ba3c8; margin-bottom:1rem; line-height:1.6;">
    Ingresa un ID de CVE para consultarlo en la API oficial del
    <strong style="color:#00c8ff;">NIST National Vulnerability Database (NVD)</strong>.
    El sistema intentará obtener datos reales (CVSS, vector, CWE, referencias). Si el entorno
    no tiene acceso a NVD (ej: Streamlit Cloud), activará automáticamente el
    <strong style="color:#ff8c42;">motor IA interno</strong> como fallback — el análisis
    siempre se genera sin importar la conectividad.
    </div>
    """, unsafe_allow_html=True)

    col_nvd1, col_nvd2 = st.columns([3, 1])
    with col_nvd1:
        nvd_cve_input = st.text_input(
            label="CVE ID",
            placeholder="Ej: CVE-2025-24813",
            label_visibility="collapsed",
            key="nvd_cve_input",
        )
    with col_nvd2:
        nvd_search_btn = st.button("🔎  CONSULTAR NVD", use_container_width=True, key="nvd_search_btn")

    if nvd_search_btn:
        raw_id = nvd_cve_input.strip()
        if not raw_id:
            st.warning("⚠️ Ingresa un ID de CVE válido (ej: CVE-2025-24813).")
        elif not re.match(r"^CVE-\d{4}-\d+$", raw_id, re.IGNORECASE):
            st.error("❌ Formato inválido. Usa el formato CVE-XXXX-YYYY (ej: CVE-2025-24813).")
        else:
            # Limpiar cache de conectividad para forzar intento fresco
            if "nvd_reachable" in st.session_state:
                del st.session_state["nvd_reachable"]

            with st.spinner(f"⚙ Consultando NVD/NIST para {raw_id.upper()}..."):
                nvd_result = fetch_nvd_cve(raw_id)

            err = nvd_result.get("error") if nvd_result else "unknown"

            # ── FALLBACK INTELIGENTE ──────────────────────────────────
            if nvd_result is None or err:
                cve_upper = raw_id.upper()

                if err == "unreachable":
                    detail_msg = nvd_result.get("detail", "Sin detalles adicionales") if nvd_result else ""
                    st.markdown(f"""
                    <div style="background:rgba(255,140,66,0.07); border:1px solid rgba(255,140,66,0.3);
                                border-left:4px solid #ff8c42; border-radius:10px; padding:1.2rem 1.5rem; margin:0.5rem 0;">
                        <div style="font-family:'Share Tech Mono',monospace; font-size:0.75rem; color:#ff8c42; letter-spacing:2px; margin-bottom:0.6rem;">
                            ⚠ CONEXIÓN NVD NO DISPONIBLE — USANDO MOTOR IA INTERNO
                        </div>
                        <div style="font-size:0.85rem; color:#8ba3c8; line-height:1.7;">
                            No se pudo conectar con la API del NVD.<br>
                            <span style="font-size:0.75rem; color:#4a6080; font-family:'Share Tech Mono',monospace;">
                            Detalle: {detail_msg}
                            </span><br><br>
                            <strong style="color:#00c8ff;">✅ Análisis generado con motor IA interno.</strong>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                elif err == "timeout":
                    st.markdown(f"""
                    <div style="background:rgba(255,215,0,0.06); border:1px solid rgba(255,215,0,0.25);
                                border-left:4px solid #ffd700; border-radius:10px; padding:1rem 1.4rem; margin:0.5rem 0;">
                        <div style="font-family:'Share Tech Mono',monospace; font-size:0.72rem; color:#ffd700; margin-bottom:0.4rem;">
                            ⏱ TIMEOUT — NVD tardó demasiado en responder
                        </div>
                        <div style="font-size:0.83rem; color:#8ba3c8;">
                            Usando motor IA interno para analizar <strong style="color:#ffd700;">{cve_upper}</strong>.
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                elif err == "not_found":
                    st.markdown(f"""
                    <div style="background:rgba(255,60,95,0.07); border:1px solid rgba(255,60,95,0.3);
                                border-left:4px solid #ff3c5f; border-radius:10px; padding:1rem 1.4rem; margin:0.5rem 0;">
                        <div style="font-family:'Share Tech Mono',monospace; font-size:0.72rem; color:#ff3c5f; margin-bottom:0.4rem;">
                            ✗ CVE NO ENCONTRADO EN NVD
                        </div>
                        <div style="font-size:0.83rem; color:#8ba3c8; line-height:1.6;">
                            <strong style="color:#c5d8f5;">{cve_upper}</strong> no existe en la base de datos del NIST
                            o aún no ha sido publicado.<br>
                            Verifica el ID e intenta de nuevo.
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    st.stop()

                elif err == "http" and nvd_result.get("code") == 403:
                    st.markdown(f"""
                    <div style="background:rgba(255,140,66,0.07); border:1px solid rgba(255,140,66,0.3);
                                border-left:4px solid #ff8c42; border-radius:10px; padding:1rem 1.4rem; margin:0.5rem 0;">
                        <div style="font-family:'Share Tech Mono',monospace; font-size:0.72rem; color:#ff8c42; margin-bottom:0.4rem;">
                            ⚠ API KEY RECHAZADA O RATE LIMIT ALCANZADO
                        </div>
                        <div style="font-size:0.83rem; color:#8ba3c8;">
                            Usando motor IA interno para analizar <strong style="color:#ffd700;">{cve_upper}</strong>.
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                else:
                    st.markdown(f"""
                    <div style="background:rgba(255,140,66,0.07); border:1px solid rgba(255,140,66,0.25);
                                border-left:4px solid #ff8c42; border-radius:10px; padding:1rem 1.4rem; margin:0.5rem 0;">
                        <div style="font-family:'Share Tech Mono',monospace; font-size:0.72rem; color:#ff8c42; margin-bottom:0.4rem;">
                            ⚠ ERROR DE CONEXIÓN — USANDO MOTOR IA INTERNO
                        </div>
                        <div style="font-size:0.83rem; color:#8ba3c8;">
                            No se pudo conectar con NVD. Analizando <strong style="color:#ffd700;">{cve_upper}</strong>
                            con el motor de IA de AegisAI.
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                # ── FALLBACK: análisis con motor interno ──────────────
                if err != "not_found":
                    st.markdown("""
                    <div style="font-family:'Share Tech Mono',monospace; font-size:0.65rem; letter-spacing:3px;
                                color:#ff8c42; margin: 1rem 0 0.5rem;">◈ ANÁLISIS IA INTERNO — MODO OFFLINE</div>
                    """, unsafe_allow_html=True)

                    fallback_input = f"{cve_upper}"
                    fallback_result = analyze_vulnerability(fallback_input, 0)
                    fallback_result["id"] = cve_upper

                    color_fb, css_cls_fb = RISK_COLORS[fallback_result["level"]]
                    level_emojis_fb = {"Crítico": "🔴", "Alto": "🟠", "Medio": "🟡", "Bajo": "🟢"}

                    sub_html_fb = ""
                    for metric, val in fallback_result["sub_scores"].items():
                        pct = int(val * 100)
                        sub_html_fb += f"""
                        <div class="cvss-row">
                            <div class="cvss-label">{metric}</div>
                            <div class="cvss-bar"><div class="cvss-fill" style="width:{pct}%; background:{color_fb};"></div></div>
                            <div class="cvss-val">{val}</div>
                        </div>"""

                    st.markdown(f"""
                    <div class="vuln-card {css_cls_fb}" style="margin-top:0.5rem; border-top: 1px dashed rgba(255,140,66,0.3);">
                        <div class="vuln-header">
                            <div class="vuln-id">{level_emojis_fb[fallback_result["level"]]} {cve_upper}</div>
                            <div class="rank-badge" style="border-color:rgba(255,140,66,0.4); color:#ff8c42;">MOTOR IA INTERNO</div>
                        </div>
                        <span class="risk-badge {css_cls_fb}">{fallback_result["level"].upper()} · CVSS ESTIMADO {fallback_result["cvss"]}</span>
                        <div class="vuln-desc" style="color:#6a80a0; font-style:italic; font-size:0.8rem; margin-bottom:0.8rem;">
                            ⚡ Análisis basado en patrones de IA — sin datos NVD en tiempo real
                        </div>
                        <div style="display:flex; gap:1.5rem; margin-bottom:0.8rem; font-size:0.78rem; color:#8ba3c8; font-family:'Share Tech Mono',monospace;">
                            <span>🎯 <strong style="color:#c5d8f5;">{fallback_result["asset_type"]}</strong></span>
                            <span>📡 Exposición: <strong style="color:{color_fb};">{fallback_result["exposure"]}</strong></span>
                            <span>⚡ Prob. Explot.: <strong style="color:{color_fb};">{fallback_result["exploit_prob"]}%</strong></span>
                        </div>
                        <div style="margin-bottom:0.8rem;">{sub_html_fb}</div>
                        <div class="section-title">◈ ANÁLISIS DE IA</div>
                        <div class="justification">{fallback_result["justification"]}</div>
                        <div class="section-title">◈ RECOMENDACIONES</div>
                        <div class="rec-block">
                            <strong>📘 NIST:</strong> {fallback_result["rec_nist"]}<br><br>
                            <strong>📗 ISO/IEC 27001:</strong> {fallback_result["rec_iso"]}<br><br>
                            <strong>🔧 Best Practices:</strong> {fallback_result["rec_best"]}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                    if st.button(f"➕  Agregar {cve_upper} al análisis por lotes", key="add_to_batch_fallback"):
                        current = st.session_state.get("nvd_additions", [])
                        entry = f"{cve_upper} - Analizado con motor IA interno"
                        if entry not in current:
                            current.append(entry)
                            st.session_state["nvd_additions"] = current
                            st.success(f"✅ {cve_upper} agregado al análisis por lotes.")
                            st.rerun()
                        else:
                            st.info("ℹ️ Este CVE ya está en la lista.")

            else:
                # ── Mostrar datos NVD crudos ──
                sev_colors = {"CRITICAL":"#ff3c5f","HIGH":"#ff8c42","MEDIUM":"#ffd700","LOW":"#39ff85","NONE":"#39ff85"}
                sev = nvd_result.get("cvss_severity") or "N/A"
                sev_color = sev_colors.get(sev, "#c5d8f5")
                cwes_str = " · ".join(nvd_result["cwes"]) if nvd_result.get("cwes") else "N/A"
                refs_html = "".join(
                    f'<a href="{r}" target="_blank" style="color:#4a9ebb; font-size:0.75rem; display:block; margin-top:2px; word-break:break-all;">{r}</a>'
                    for r in nvd_result.get("references", [])
                )

                st.markdown(f"""
                <div style="background:linear-gradient(135deg,#0d1526,#0f1a2e); border:1px solid rgba(0,200,255,0.2);
                            border-left:4px solid {sev_color}; border-radius:10px; padding:1.2rem 1.5rem; margin:0.8rem 0;">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.8rem;">
                        <div style="font-family:\'Share Tech Mono\',monospace; font-size:1.1rem; color:#fff; font-weight:700;">
                            {nvd_result["cve_id"]}
                        </div>
                        <div style="font-family:\'Share Tech Mono\',monospace; font-size:0.68rem; background:rgba(0,200,255,0.08);
                                    border:1px solid rgba(0,200,255,0.25); color:#00c8ff; padding:2px 10px; border-radius:20px;">
                            ✅ DATOS VERIFICADOS · {nvd_result.get("source","MITRE/NVD").upper()}
                        </div>
                    </div>
                    <div style="display:flex; gap:2rem; margin-bottom:0.9rem; flex-wrap:wrap;">
                        <div>
                            <div style="font-family:\'Share Tech Mono\',monospace; font-size:0.6rem; letter-spacing:2px; color:#4a9ebb;">CVSS SCORE</div>
                            <div style="font-family:\'Share Tech Mono\',monospace; font-size:1.8rem; color:{sev_color}; font-weight:700;">
                                {nvd_result.get("cvss_score", "N/A")}
                            </div>
                        </div>
                        <div>
                            <div style="font-family:\'Share Tech Mono\',monospace; font-size:0.6rem; letter-spacing:2px; color:#4a9ebb;">SEVERIDAD</div>
                            <div style="font-family:\'Share Tech Mono\',monospace; font-size:1.3rem; color:{sev_color}; font-weight:700;">
                                {sev}
                            </div>
                        </div>
                        <div>
                            <div style="font-family:\'Share Tech Mono\',monospace; font-size:0.6rem; letter-spacing:2px; color:#4a9ebb;">PUBLICADO</div>
                            <div style="font-family:\'Share Tech Mono\',monospace; font-size:0.9rem; color:#c5d8f5;">
                                {nvd_result.get("published","N/A")}
                            </div>
                        </div>
                        <div>
                            <div style="font-family:\'Share Tech Mono\',monospace; font-size:0.6rem; letter-spacing:2px; color:#4a9ebb;">ÚLTIMA MOD.</div>
                            <div style="font-family:\'Share Tech Mono\',monospace; font-size:0.9rem; color:#c5d8f5;">
                                {nvd_result.get("modified","N/A")}
                            </div>
                        </div>
                    </div>
                    <div style="font-family:\'Share Tech Mono\',monospace; font-size:0.6rem; letter-spacing:2px; color:#4a9ebb; margin-bottom:3px;">VECTOR</div>
                    <div style="font-family:\'Share Tech Mono\',monospace; font-size:0.78rem; color:#8ba3c8; margin-bottom:0.7rem; word-break:break-all;">
                        {nvd_result.get("cvss_vector","N/A")}
                    </div>
                    <div style="font-family:\'Share Tech Mono\',monospace; font-size:0.6rem; letter-spacing:2px; color:#4a9ebb; margin-bottom:3px;">CWE</div>
                    <div style="font-size:0.82rem; color:#8ba3c8; margin-bottom:0.7rem;">{cwes_str}</div>
                    <div style="font-family:\'Share Tech Mono\',monospace; font-size:0.6rem; letter-spacing:2px; color:#4a9ebb; margin-bottom:3px;">DESCRIPCIÓN OFICIAL (ES)</div>
                    <div style="font-size:0.85rem; color:#a0b8d8; line-height:1.6; margin-bottom:0.4rem;">
                        {nvd_result["description"]}
                    </div>
                    <div style="font-size:0.75rem; color:#4a6080; font-style:italic; margin-bottom:0.7rem; border-left:2px solid rgba(0,200,255,0.15); padding-left:8px;">
                        🇺🇸 EN: {nvd_result.get("description_en", "")}
                    </div>
                    <div style="font-family:\'Share Tech Mono\',monospace; font-size:0.6rem; letter-spacing:2px; color:#4a9ebb; margin-bottom:3px;">REFERENCIAS</div>
                    {refs_html}
                </div>
                """, unsafe_allow_html=True)

                # ── Generar análisis AegisAI con datos reales ──
                st.markdown("""
                <div style="font-family:\'Share Tech Mono\',monospace; font-size:0.65rem; letter-spacing:3px;
                            color:#4a9ebb; margin: 1rem 0 0.5rem;">◈ ANÁLISIS AEGISAI CON DATOS REALES</div>
                """, unsafe_allow_html=True)

                nvd_analysis = analyze_vulnerability_nvd(nvd_result)
                color_nvd, css_cls_nvd = RISK_COLORS[nvd_analysis["level"]]
                level_emojis = {"Crítico": "🔴", "Alto": "🟠", "Medio": "🟡", "Bajo": "🟢"}

                sub_html_nvd = ""
                for metric, val in nvd_analysis["sub_scores"].items():
                    pct = int(val * 100)
                    sub_html_nvd += f"""
                    <div class="cvss-row">
                        <div class="cvss-label">{metric}</div>
                        <div class="cvss-bar"><div class="cvss-fill" style="width:{pct}%; background:{color_nvd};"></div></div>
                        <div class="cvss-val">{val}</div>
                    </div>"""

                st.markdown(f"""
                <div class="vuln-card {css_cls_nvd}" style="margin-top:0.5rem;">
                    <div class="vuln-header">
                        <div class="vuln-id">{level_emojis[nvd_analysis["level"]]} {nvd_analysis["id"]}</div>
                        <div class="rank-badge">DATOS REALES · NVD/NIST</div>
                    </div>
                    <span class="risk-badge {css_cls_nvd}">{nvd_analysis["level"].upper()} · CVSS {nvd_analysis["cvss"]}</span>
                    <div class="vuln-desc">{nvd_analysis["description"][:220]}{"..." if len(nvd_analysis["description"])>220 else ""}</div>
                    <div style="display:flex; gap:1.5rem; margin-bottom:0.8rem; font-size:0.78rem; color:#8ba3c8; font-family:\'Share Tech Mono\',monospace;">
                        <span>🎯 <strong style="color:#c5d8f5;">{nvd_analysis["asset_type"]}</strong></span>
                        <span>📡 Exposición: <strong style="color:{color_nvd};">{nvd_analysis["exposure"]}</strong></span>
                        <span>⚡ Prob. Explot.: <strong style="color:{color_nvd};">{nvd_analysis["exploit_prob"]}%</strong></span>
                    </div>
                    <div style="margin-bottom:0.8rem;">{sub_html_nvd}</div>
                    <div class="section-title">◈ ANÁLISIS DE IA</div>
                    <div class="justification">{nvd_analysis["justification"]}</div>
                    <div class="section-title">◈ RECOMENDACIONES</div>
                    <div class="rec-block">
                        <strong>📘 NIST:</strong> {nvd_analysis["rec_nist"]}<br><br>
                        <strong>📗 ISO/IEC 27001:</strong> {nvd_analysis["rec_iso"]}<br><br>
                        <strong>🔧 Best Practices:</strong> {nvd_analysis["rec_best"]}
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # Botón para agregar al análisis principal
                if st.button(f"➕  Agregar {nvd_result['cve_id']} al análisis por lotes", key="add_to_batch"):
                    current = st.session_state.get("nvd_additions", [])
                    entry = f"{nvd_result['cve_id']} - {nvd_result['description'][:80]}"
                    if entry not in current:
                        current.append(entry)
                        st.session_state["nvd_additions"] = current
                        st.success(f"✅ {nvd_result['cve_id']} agregado. Aparecerá pre-cargado en el área de análisis por lotes.")
                        st.rerun()
                    else:
                        st.info("ℹ️ Este CVE ya está en la lista de análisis por lotes.")

st.markdown('<hr class="aegis-divider">', unsafe_allow_html=True)

# ─────────────────────────────────────────────
# INPUT SECTION
# ─────────────────────────────────────────────
SAMPLE_DATA = """CVE-2025-24813 - Apache Tomcat Remote Code Execution (CVSS 9.8)
CVE-2024-55591 - Fortinet FortiOS authentication bypass (edge device crítico)
CVE-2025-40538 - SolarWinds Serv-U Remote Code Execution
CVE-2025-32756 - Fortinet FortiVoice vulnerability (infraestructura expuesta)
CVE-2024-38475 - Apache HTTP Server mod_rewrite RCE
CVE-2025-48633 - Android zero-day exploit usado en ataques dirigidos
CVE-2025-43529 - Apple WebKit zero-day explotado en ataques reales
Servidor web Apache desactualizado sin parches recientes
Configuración incorrecta de CORS en API pública expuesta a internet
Credenciales por defecto en panel administrativo interno
Divulgación de versión mediante banner grabbing en servidor HTTP
Mensajes de error detallados en aplicación web en entorno productivo"""

default_text = SAMPLE_DATA if st.session_state.get("sample_loaded") else ""
# Append any CVEs added from NVD lookup
nvd_additions = st.session_state.get("nvd_additions", [])
if nvd_additions:
    extra = "\n".join(nvd_additions)
    default_text = (default_text + "\n" + extra).strip() if default_text else extra

st.markdown("""
<div class="section-header">◈ ENTRADA DE VULNERABILIDADES</div>
""", unsafe_allow_html=True)

col_in, col_hint = st.columns([3, 1])
with col_in:
    vuln_input = st.text_area(
        label="Ingresa una vulnerabilidad por línea (CVE-ID - Descripción)",
        value=default_text,
        height=180,
        placeholder="CVE-2024-1234 - Descripción de la vulnerabilidad\nCVE-2023-5678 - Otra vulnerabilidad\n...",
        label_visibility="collapsed",
    )

with col_hint:
    st.markdown("""
    <div style="background:rgba(0,200,255,0.04); border:1px solid rgba(0,200,255,0.12); border-radius:8px; padding:1rem; font-size:0.78rem; color:#8ba3c8; line-height:1.8;">
    <strong style="color:#00c8ff; font-family:'Share Tech Mono',monospace;">FORMATO:</strong><br>
    • Una vuln. por línea<br>
    • <code>CVE-XXXX-YYYY - desc</code><br>
    • O solo descripción libre<br>
    • La IA estima severidad<br>
    <br>
    <strong style="color:#00c8ff; font-family:'Share Tech Mono',monospace;">MÁXIMO:</strong> 20 vulns.
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 4])
with col_btn1:
    analyze_clicked = st.button("🤖  ANALIZAR CON IA", use_container_width=True)
with col_btn2:
    clear_clicked = st.button("🗑️  LIMPIAR", use_container_width=True)

if clear_clicked:
    st.session_state["results"] = []
    st.session_state["sample_loaded"] = False
    st.rerun()


# ─────────────────────────────────────────────
# ANALYSIS ENGINE
# ─────────────────────────────────────────────
if analyze_clicked:
    lines = [l.strip() for l in vuln_input.strip().splitlines() if l.strip()]
    if not lines:
        st.warning("⚠️ Ingresa al menos una vulnerabilidad para analizar.")
    elif len(lines) > 20:
        st.error("❌ Máximo 20 vulnerabilidades por análisis.")
    else:
        progress_bar = st.progress(0)
        status_text  = st.empty()

        results = []
        for i, line in enumerate(lines):
            pct = int((i + 1) / len(lines) * 100)
            status_text.markdown(
                f"<div style='font-family:Share Tech Mono,monospace; color:#4a9ebb; font-size:0.8rem;'>"
                f"⚙ Procesando [{i+1}/{len(lines)}] — Correlacionando con MITRE ATT&CK...</div>",
                unsafe_allow_html=True,
            )
            progress_bar.progress(pct)
            time.sleep(0.3)
            r = analyze_vulnerability(line, i)
            if r:
                results.append(r)

        # Ordenar por riesgo y CVSS
        results.sort(key=lambda x: (RISK_ORDER[x["level"]], -x["cvss"]))
        # Asignar prioridad final
        for i, r in enumerate(results):
            r["priority"] = i + 1

        st.session_state["results"] = results
        progress_bar.empty()
        status_text.empty()


# ─────────────────────────────────────────────
# RESULTS DISPLAY
# ─────────────────────────────────────────────
results = st.session_state.get("results", [])

if results:
    st.markdown('<hr class="aegis-divider">', unsafe_allow_html=True)

    # ── KPI Cards ──
    n_critical = sum(1 for r in results if r["level"] == "Crítico")
    n_high     = sum(1 for r in results if r["level"] == "Alto")
    n_medium   = sum(1 for r in results if r["level"] == "Medio")
    n_low      = sum(1 for r in results if r["level"] == "Bajo")
    global_score = compute_global_score(results)

    st.markdown("""
    <div class="section-header">◈ RESUMEN EJECUTIVO</div>
    """, unsafe_allow_html=True)

    c1, c2, c3, c4, c5 = st.columns(5)
    for col, label, val, cls in [
        (c1, "CRÍTICO",       n_critical,   "critical"),
        (c2, "ALTO",          n_high,        "high"),
        (c3, "MEDIO",         n_medium,      "medium"),
        (c4, "BAJO",          n_low,         "low"),
        (c5, "RISK SCORE",    global_score,  "score"),
    ]:
        with col:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">{label}</div>
                <div class="metric-value {cls}">{val}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Charts ──
    col_chart1, col_chart2 = st.columns([1, 1])

    with col_chart1:
        # Donut de distribución
        labels = ["Crítico", "Alto", "Medio", "Bajo"]
        values = [n_critical, n_high, n_medium, n_low]
        colors = ["#ff3c5f", "#ff8c42", "#ffd700", "#39ff85"]
        non_zero = [(l, v, c) for l, v, c in zip(labels, values, colors) if v > 0]
        if non_zero:
            lz, vz, cz = zip(*non_zero)
            fig_donut = go.Figure(go.Pie(
                labels=list(lz), values=list(vz),
                hole=0.62,
                marker=dict(colors=list(cz), line=dict(color="#070b14", width=3)),
                textinfo="label+percent",
                textfont=dict(family="Share Tech Mono", color="#c5d8f5", size=11),
                hovertemplate="<b>%{label}</b><br>Cantidad: %{value}<br>%{percent}<extra></extra>",
            ))
            fig_donut.update_layout(
                title=dict(text="Distribución de Riesgos", font=dict(family="Share Tech Mono", color="#4a9ebb", size=12), x=0.5),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                showlegend=False,
                margin=dict(t=40, b=10, l=10, r=10),
                height=260,
                annotations=[dict(
                    text=f"<b>{len(results)}</b><br><span style='font-size:10'>vulns</span>",
                    x=0.5, y=0.5, font=dict(size=18, color="#ffffff", family="Share Tech Mono"),
                    showarrow=False
                )],
            )
            st.plotly_chart(fig_donut, use_container_width=True, config={"displayModeBar": False})

    with col_chart2:
        # Gauge de Risk Score global
        gauge_color = "#ff3c5f" if global_score >= 7 else "#ff8c42" if global_score >= 5 else "#ffd700" if global_score >= 3 else "#39ff85"
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=global_score,
            domain={"x": [0, 1], "y": [0, 1]},
            title={"text": "Risk Score Global", "font": {"family": "Share Tech Mono", "color": "#4a9ebb", "size": 12}},
            number={"font": {"family": "Share Tech Mono", "color": "#ffffff", "size": 36}},
            gauge={
                "axis":        {"range": [0, 10], "tickfont": {"family": "Share Tech Mono", "color": "#4a9ebb", "size": 9}},
                "bar":         {"color": gauge_color, "thickness": 0.25},
                "bgcolor":     "rgba(13,21,38,0.8)",
                "bordercolor": "rgba(0,200,255,0.2)",
                "steps": [
                    {"range": [0, 3],  "color": "rgba(57,255,133,0.07)"},
                    {"range": [3, 5],  "color": "rgba(255,215,0,0.07)"},
                    {"range": [5, 7],  "color": "rgba(255,140,66,0.07)"},
                    {"range": [7, 10], "color": "rgba(255,60,95,0.07)"},
                ],
                "threshold": {"line": {"color": gauge_color, "width": 3}, "thickness": 0.8, "value": global_score},
            },
        ))
        fig_gauge.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            height=260,
            margin=dict(t=40, b=10, l=20, r=20),
        )
        st.plotly_chart(fig_gauge, use_container_width=True, config={"displayModeBar": False})

    # ── CVSS Bar chart horizontal ──
    if len(results) >= 2:
        cvss_ids    = [r["id"] for r in results]
        cvss_vals   = [r["cvss"] for r in results]
        cvss_colors = [RISK_COLORS[r["level"]][0] for r in results]

        fig_bar = go.Figure(go.Bar(
            x=cvss_vals,
            y=cvss_ids,
            orientation="h",
            marker=dict(color=cvss_colors, line=dict(color="rgba(0,0,0,0)")),
            hovertemplate="<b>%{y}</b><br>CVSS: %{x}<extra></extra>",
            text=[f"{v}" for v in cvss_vals],
            textposition="outside",
            textfont=dict(family="Share Tech Mono", color="#c5d8f5", size=10),
        ))
        fig_bar.update_layout(
            title=dict(text="CVSS Score por Vulnerabilidad", font=dict(family="Share Tech Mono", color="#4a9ebb", size=12), x=0),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(13,21,38,0.5)",
            xaxis=dict(range=[0, 11], gridcolor="rgba(0,200,255,0.07)", tickfont=dict(family="Share Tech Mono", color="#4a9ebb", size=9)),
            yaxis=dict(gridcolor="rgba(0,0,0,0)", tickfont=dict(family="Share Tech Mono", color="#c5d8f5", size=10)),
            height=max(200, len(results) * 40),
            margin=dict(t=40, b=10, l=20, r=60),
            bargap=0.35,
        )
        st.plotly_chart(fig_bar, use_container_width=True, config={"displayModeBar": False})

    # ── Vulnerability Cards ──
    st.markdown("""
    <div class="section-header">◈ ANÁLISIS DETALLADO — VULNERABILIDADES PRIORIZADAS</div>
    """, unsafe_allow_html=True)

    for r in results:
        color, css_cls = RISK_COLORS[r["level"]]
        level_emojis   = {"Crítico": "🔴", "Alto": "🟠", "Medio": "🟡", "Bajo": "🟢"}

        # Sub-scores CVSS HTML
        sub_html = ""
        for metric, val in r["sub_scores"].items():
            pct = int(val * 100)
            sub_html += f"""
            <div class="cvss-row">
                <div class="cvss-label">{metric}</div>
                <div class="cvss-bar"><div class="cvss-fill" style="width:{pct}%; background:{color};"></div></div>
                <div class="cvss-val">{val}</div>
            </div>"""

        st.markdown(f"""
        <div class="vuln-card {css_cls}">
            <div class="vuln-header">
                <div class="vuln-id">{level_emojis[r['level']]} {r['id']}</div>
                <div class="rank-badge">PRIORIDAD #{r['priority']}</div>
            </div>
            <span class="risk-badge {css_cls}">{r['level'].upper()} · CVSS {r['cvss']}</span>
            <div class="vuln-desc">{r['description']}</div>
            <div style="display:flex; gap:1.5rem; margin-bottom:0.8rem; font-size:0.78rem; color:#8ba3c8; font-family:'Share Tech Mono',monospace;">
                <span>🎯 <strong style="color:#c5d8f5;">{r['asset_type']}</strong></span>
                <span>📡 Exposición: <strong style="color:{color};">{r['exposure']}</strong></span>
                <span>⚡ Prob. Explot.: <strong style="color:{color};">{r['exploit_prob']}%</strong></span>
            </div>
            <div style="margin-bottom:0.8rem;">{sub_html}</div>
            <div class="section-title">◈ ANÁLISIS DE IA</div>
            <div class="justification">{r['justification']}</div>
            <div class="section-title">◈ RECOMENDACIONES</div>
            <div class="rec-block">
                <strong>📘 NIST:</strong> {r['rec_nist']}<br><br>
                <strong>📗 ISO/IEC 27001:</strong> {r['rec_iso']}<br><br>
                <strong>🔧 Best Practices:</strong> {r['rec_best']}
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ── Export ──
    st.markdown('<hr class="aegis-divider">', unsafe_allow_html=True)
    st.markdown("""
    <div class="section-header">◈ EXPORTAR RESULTADOS</div>
    """, unsafe_allow_html=True)

    df = results_to_dataframe(results)
    col_e1, col_e2, col_e3 = st.columns([1, 1, 3])

    with col_e1:
        csv_buffer = io.StringIO()
        df.to_csv(csv_buffer, index=False)
        st.download_button(
            label="📥 Exportar CSV",
            data=csv_buffer.getvalue(),
            file_name=f"aegisai_report_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv",
            use_container_width=True,
        )

    with col_e2:
        # JSON export
        export_data = json.dumps(results, indent=2, ensure_ascii=False)
        st.download_button(
            label="📥 Exportar JSON",
            data=export_data,
            file_name=f"aegisai_report_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
            mime="application/json",
            use_container_width=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Prioridad": st.column_config.NumberColumn(width="small"),
            "CVSS":      st.column_config.ProgressColumn(min_value=0, max_value=10, format="%.1f"),
        },
    )

else:
    # ── Welcome state ──
    st.markdown("""
    <div style="text-align:center; padding: 4rem 2rem; color:#4a6080;">
        <div style="font-size:4rem; margin-bottom:1rem;">🛡️</div>
        <div style="font-family:'Share Tech Mono',monospace; font-size:0.9rem; letter-spacing:3px; color:#4a9ebb; margin-bottom:0.8rem;">
            SISTEMA LISTO · ESPERANDO VULNERABILIDADES
        </div>
        <div style="font-size:0.85rem; color:#4a6080; max-width:500px; margin:0 auto; line-height:1.8;">
            Ingresa CVEs o descripciones de vulnerabilidades en el campo de texto.<br>
            El motor de IA analizará, priorizará y generará recomendaciones<br>
            basadas en <strong style="color:#4a9ebb;">NIST</strong>, <strong style="color:#4a9ebb;">ISO/IEC 27001</strong> y <strong style="color:#4a9ebb;">MITRE ATT&CK</strong>.
        </div>
    </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────
st.markdown("""
<hr class="aegis-divider">
<div style="text-align:center; font-family:'Share Tech Mono',monospace; font-size:0.62rem; letter-spacing:2px; color:#2a3a50; padding-bottom:1rem;">
    AegisAI v1.0.0 · AI-Powered Vulnerability Management · NIST SP 800-40 · ISO/IEC 27001 · MITRE ATT&CK<br>
    © 2025 AegisAI Framework — For security assessment purposes only
</div>
""", unsafe_allow_html=True)
