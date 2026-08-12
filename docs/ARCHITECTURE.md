# ARCHITECTURE

## System Architecture

RADIS follows a modern decoupled architecture:

```mermaid
graph TD;
    Client[Next.js Frontend] -->|REST API| API[FastAPI Backend];
    API --> DB[(PostgreSQL Database)];
    API --> Storage[Local / Object Storage];
    API --> AI_Engine[PyTorch / MONAI Inference Engine];
    AI_Engine --> Model_Registry[Local Model Weights];
```

## AI Architecture

The AI module is not a single black box. It is a pipeline of sequential and parallel processors:

```mermaid
graph TD;
    D[DICOM Study] --> P[Preprocessing & HU Conversion];
    P --> V[Study Validation & Windowing];
    V --> C[Classification Model];
    V --> S[Segmentation/Localization Model];
    C --> F[Finding Engine];
    S --> F;
    F --> Q[Quantitative Analysis];
    Q --> R[Clinical Rules Engine];
    R --> LLM[Report Generator];
```

## Backend Flow

1. **Upload**: User uploads DICOM ZIP.
2. **Parsing**: `pydicom` parses the headers, validates it's a Non-Contrast Brain CT.
3. **Queue/Inference**: The CT volume is passed to the AI Engine.
4. **Processing**: Results (JSON) are stored in the Database.
5. **Report**: Rules engine determines priority; structured report is drafted.
6. **Serve**: Frontend fetches the study, images, and report.

## Inference Flow
- **Data format**: 3D NIfTI or stacked 2D NumPy arrays.
- **Model**: PyTorch model outputs probabilities.
- **Thresholding**: Configurable confidence thresholds determine if a finding is presented to the user.
