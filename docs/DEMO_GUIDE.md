# RADIS — Smart India Hackathon Demo & Reviewer Guide

Welcome to the **RADIS (Radiology AI Decision Support & Reporting)** platform demo. This guide provides step-by-step instructions for judges, clinical reviewers, and developers to test the full-stack system.

---

## Quick Start (30 Seconds Setup)

### 1. Start the RADIS Server
Open PowerShell in the project directory and run:
```powershell
.\venv\Scripts\python scripts/run_demo_server.py
```
This launches the FastAPI backend and serves the interactive Workstation UI at `http://localhost:8000`.

### 2. Open the Clinical Workstation
Open your web browser and navigate to:
👉 **`http://localhost:8000`**

---

## Interactive Demo Scenarios

### Scenario A: Testing Pre-Packaged Demo Scans (Zero Upload Required)
1. On the left panel under **Upload & Queue**, click **"⚡ Load Demo Scan"**.
2. An interactive synthetic Brain CT scan (`sample_brain_ct_epidural.dcm`) will be loaded instantly.
3. Click the **"⚡ Run AI Analysis & Report"** button at the bottom of the DICOM viewer.
4. Observe the results:
   - **Pulsing Triage Badges**: `URGENCY: HIGH` | `SEVERITY: HIGH`.
   - **Workflow Recommendation**: *"STAT radiology review recommended (High Severity/Urgency detected)."*
   - **Grad-CAM & Bounding Box**: Glowing red/yellow heatmap and bounding box indicating the epidural hemorrhage location.
   - **Pathology Meters**: Probability breakdown for Epidural (94.0%), Subarachnoid (78.0%), and overall hemorrhage risk.
   - **Radiology Report**: Click the **"Radiology Report"** tab to view the live, editable markdown report.

### Scenario B: Uploading Real DICOM Scans
1. In `data/demo_scans/`, we have pre-generated sample DICOM files:
   - `data/demo_scans/epidural_hematoma_ct.dcm`
   - `data/demo_scans/subdural_hematoma_ct.dcm`
   - `data/demo_scans/subarachnoid_hemorrhage_ct.dcm`
   - `data/demo_scans/normal_brain_ct.dcm`
2. Drag and drop any `.dcm` file into the upload dropzone.
3. Click **"Run AI Analysis & Report"** to run model inference, Grad-CAM explainability, and report generation in real-time.

### Scenario C: DICOM Windowing & Visual Controls
Use the top toolbar above the canvas to test CT windowing presets:
- **Brain Window (W:80 L:40)**: Optimized for soft tissue and brain parenchyma.
- **Subdural Window (W:200 L:80)**: Optimized for subtle extra-axial fluid collections.
- **Bone Window (W:2000 L:600)**: Optimized for skull fractures.
- **Grad-CAM Overlay Toggle**: Turn heatmaps on/off.
- **Bounding Box Toggle**: Turn detection bounding boxes on/off.

### Scenario D: Report Editing & Export
1. Switch to the **"Radiology Report"** tab.
2. Edit any section in the live report editor.
3. Click **"📥 Export Markdown"** or **"📄 Export JSON"** to download the report locally.
4. Click **"✅ Sign & Approve"** to simulate clinical sign-off.

---

## Running Automated Tests

To verify all 22+ unit, API, and full-stack integration tests:
```powershell
.\venv\Scripts\python -m pytest tests/ backend/tests/ -v
```
