# 🛡️ AegisAI — AI-Powered Vulnerability Management

![Python](https://img.shields.io/badge/Python-3.9+-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.32+-red)

AegisAI es un sistema de gestión de vulnerabilidades basado en Inteligencia Artificial. Analiza, prioriza y genera recomendaciones basadas en NIST SP 800-40, ISO/IEC 27001 y MITRE ATT&CK.

---

## 🚀 Instalación

```bash
git clone https://github.com/Heist574/AegisAI.git
cd AegisAI
pip install -r requirements.txt
streamlit run aegisai_app.py
```

---

## 🎯 Funcionalidades

- Consulta CVE en tiempo real (MITRE CVEProject + NVD/NIST)
- Análisis por lotes con motor IA interno
- Priorización automática por nivel de riesgo
- Recomendaciones basadas en NIST, ISO 27001, MITRE ATT&CK
- Traducción automática al español
- Exportación CSV y JSON

---

## 🧠 Fuentes de datos

| Fuente | Descripción |
|---|---|
| MITRE CVEProject (GitHub) | Fuente primaria, sin restricciones |
| NVD/NIST API | Fuente secundaria, con API key |
| Motor IA interno | Fallback siempre disponible |

---

## 📊 Estándares aplicados

| Estándar | Uso |
|---|---|
| NIST SP 800-40 Rev.4 | Gestión de parches |
| ISO/IEC 27001:2022 | Controles de seguridad |
| MITRE ATT&CK | Correlación de amenazas |
| CVSS v3.1 | Scoring de vulnerabilidades |

---

*AegisAI v1.0 — Prototipo académico para tesis de grado*
