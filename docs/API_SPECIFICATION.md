# API SPECIFICATION

## Overview
The RADIS backend will be built with FastAPI and serve RESTful endpoints for the frontend to upload studies, request analysis, and retrieve reports.

## Base URL
`/api/v1`

## Endpoints

### 1. Studies
**`POST /studies/upload`**
- **Description**: Upload a DICOM study (ZIP file).
- **Request Format**: `multipart/form-data` with file.
- **Response Format**: `{"study_id": "...", "status": "uploaded", "slices": 128}`

**`GET /studies/{study_id}`**
- **Description**: Retrieve metadata for a specific study.
- **Response Format**: `{"study_id": "...", "modality": "CT", "body_region": "HEAD"}`

**`GET /studies/{study_id}/slices`**
- **Description**: Retrieve a list of image URLs for the viewer.
- **Response Format**: `{"slices": ["/media/...", "/media/..."]}`

### 2. Analysis
**`POST /studies/{study_id}/analyze`**
- **Description**: Trigger the AI inference pipeline on a study.
- **Request Format**: Empty POST or specific config (e.g., `{"model_version": "v1.0"}`).
- **Response Format**: `{"job_id": "...", "status": "processing"}`
- *Note: This is asynchronous.*

**`GET /studies/{study_id}/findings`**
- **Description**: Retrieve the extracted AI findings for a study.
- **Response Format**:
```json
{
  "study_id": "...",
  "findings": [
    {
      "type": "intracranial_hemorrhage",
      "location": "left basal ganglia",
      "confidence": 0.94,
      "bounding_box": [x1, y1, x2, y2],
      "slice_index": 63
    }
  ]
}
```

### 3. Reports
**`POST /studies/{study_id}/report`**
- **Description**: Generate a preliminary structured report based on current findings.
- **Response Format**: `{"report_id": "...", "text": "EXAMINATION...", "status": "draft"}`

**`PUT /reports/{report_id}`**
- **Description**: Update the report (Radiologist edit).
- **Request Format**: `{"text": "Edited text..."}`

**`POST /reports/{report_id}/finalize`**
- **Description**: Lock the report as finalized by the clinician.

## Error Handling
- Standard HTTP status codes (400 Bad Request, 404 Not Found, 500 Internal Server Error).
- All errors return a JSON payload: `{"error": "Description of error"}`.

## Security
- For the MVP, endpoints might be open locally. If deployed, JWT-based authentication will be enforced.
