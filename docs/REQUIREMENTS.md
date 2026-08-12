# REQUIREMENTS

## Functional Requirements

1. **DICOM Upload & Parsing**
   - System must accept DICOM files/folders/ZIPs.
   - System must extract metadata: modality, study ID, series ID, body region, pixel spacing, etc.
   - System must de-identify or avoid exposing patient identifying data on the UI.

2. **CT Preprocessing**
   - System must convert pixel data to Hounsfield Units (HU).
   - System must apply appropriate clinical windowing (e.g., brain window, bone window).

3. **AI Inference**
   - System must classify the presence of specified abnormalities (e.g., intracranial hemorrhage).
   - System must provide localization (bounding box or segmentation) for positive findings.
   - System must generate a confidence score for its predictions.

4. **Clinical Decision Support (CDS)**
   - System must evaluate AI findings against rule-based logic to suggest an urgency level.
   - System must provide a suggested workflow/follow-up pathway.

5. **Report Generation**
   - System must generate a preliminary structured report based on AI findings.
   - The UI must allow a radiologist to edit, accept, or reject findings.

6. **Medical Viewer (Frontend)**
   - System must provide an interface to view CT slices.
   - Viewer must support zoom, pan, window/level adjustments, and slice navigation.
   - Viewer must display AI overlays (localization/segmentation).

## Non-Functional Requirements

1. **Performance**
   - End-to-end inference for a single Brain CT study should ideally complete in under 2 minutes to provide value in a triage setting.

2. **Security & Privacy**
   - Implementation of basic prototype security: no patient PHI logged permanently, secure file handling.
   - Ensure external APIs (like LLMs) are NOT sent patient PHI.

3. **Modularity**
   - The AI models must be modular and versioned to allow swapping in improved models or new modalities later.

4. **Safety & Ethics**
   - UI must permanently display that it is an AI-assisted tool requiring professional verification.
   - The AI must default to "uncertain" or flag for manual review if confidence is below a threshold.
