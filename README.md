# RADIS — Radiology AI Decision Intelligence System

> **AI-assisted radiology decision support & reporting platform with mandatory human verification.**

RADIS is a production-grade AI workstation (built for Smart India Hackathon) designed to assist radiologists in analyzing medical imaging studies. The system focuses on detecting, localizing, prioritizing, and generating reports for **Intracranial Hemorrhage (ICH)** on Non-Contrast Brain CTs.

---

## ⚠️ Medical Safety Disclaimer
**AI-assisted decision support only. This system is a research prototype and is not a substitute for a licensed radiologist or qualified healthcare professional. AI-generated findings and reports require professional verification before clinical use.**

---

## 🚀 Quick Start (One Command Launch)

### 1. Launch Server & Workstation
```powershell
.\venv\Scripts\python scripts/run_demo_server.py
```
Open **`http://localhost:8000`** in your browser to access the Clinical Workstation UI.

### 2. Run Test Suite (25 Tests)
```powershell
.\venv\Scripts\python -m pytest tests/ backend/tests/ -v
```

---

## ✨ Key Capabilities

- **Multi-Window DICOM Processing**: Parses `.dcm` CT scans and applies Brain (W:80 L:40), Subdural (W:200 L:80), and Bone (W:2000 L:600) clinical Hounsfield windowing.
- **Multi-Label AI Classifier**: ResNet-50 backbone predicting 6 hemorrhage classes (`any`, `epidural`, `intraparenchymal`, `intraventricular`, `subarachnoid`, `subdural`).
- **Grad-CAM & Bounding Box Localization**: Heatmap overlays and bounding box coordinate extraction for explainability.
- **Clinical Decision Support Engine**: Rule-based severity (`HIGH`/`MEDIUM`/`LOW`) and urgency (`STAT`/`PRIORITY`/`ROUTINE`) calculation.
- **Structured Radiology Report Generator**: Synthesizes formal medical findings and impressions into validated Markdown/JSON.
- **Glassmorphic Workstation UI**: Interactive HTML5 Canvas viewer with DICOM presets, overlay toggles, pathology meters, and live report editor.

---

## 🛠️ Architecture & Documentation

- [SIH Pitch & Architecture](file:///docs/ARCHITECTURE_AND_PITCH.md) (`docs/ARCHITECTURE_AND_PITCH.md`)
- [Judge & Reviewer Demo Guide](file:///docs/DEMO_GUIDE.md) (`docs/DEMO_GUIDE.md`)
- [Dataset Strategy](file:///docs/DATASET_PLAN.md) (`docs/DATASET_PLAN.md`)
- [Medical Safety Framework](file:///docs/MEDICAL_SAFETY.md) (`docs/MEDICAL_SAFETY.md`)

---

## 💻 Tech Stack

- **Frontend**: HTML5, CSS3 Glassmorphism Design System, JavaScript (ES6 Canvas API)
- **Backend API**: FastAPI, Uvicorn, Pydantic v2, Python 3.14
- **AI/ML & Vision**: PyTorch 2.13, OpenCV, PyDICOM, MONAI, Scikit-Learn
- **Testing**: Pytest, FastAPI TestClient

---

## 📊 Development Status
All 11 roadmap phases are **100% Completed**. See `planning/CURRENT_PHASE.md` and `planning/TASKS.md` for execution history.
