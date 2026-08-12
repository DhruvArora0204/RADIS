import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "RADIS Backend API"}

def test_upload_invalid_file():
    response = client.post(
        "/api/v1/scans/upload",
        files={"file": ("test.txt", b"dummy content", "text/plain")}
    )
    assert response.status_code == 400
    assert "Only DICOM (.dcm) files are supported" in response.json()["detail"]

def test_upload_valid_dicom_filename():
    response = client.post(
        "/api/v1/scans/upload",
        files={"file": ("sample.dcm", b"mock dicom binary content", "application/dicom")}
    )
    assert response.status_code == 201
    data = response.json()
    assert "scan_id" in data
    assert data["filename"] == "sample.dcm"
    assert data["status"] == "uploaded"

def test_list_scans():
    response = client.get("/api/v1/scans")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_nonexistent_scan():
    response = client.get("/api/v1/scans/NONEXISTENT-123")
    assert response.status_code == 404

def test_analyze_scan_endpoint(mocker=None):
    from unittest.mock import patch
    upload_res = client.post(
        "/api/v1/scans/upload",
        files={"file": ("test_brain.dcm", b"mock binary", "application/dicom")}
    )
    assert upload_res.status_code == 201
    scan_id = upload_res.json()["scan_id"]

    mock_pipeline_result = {
        "decision_support": {
            "findings": [{"label": "epidural", "probability": 0.9, "bounding_box": (10, 10, 50, 50)}],
            "assessment": {
                "urgency_level": "HIGH",
                "severity_level": "HIGH",
                "workflow_recommendation": "STAT radiology review recommended."
            },
            "timestamp": "2026-08-11T00:00:00Z"
        },
        "radiology_report": {
          "study_id": scan_id,
          "patient_id": "ANONYMOUS",
          "clinical_history": "Evaluation",
          "technique": "CT",
          "findings_section": ["Epidural hemorrhage"],
          "impression_section": ["High severity"],
          "severity_level": "HIGH",
          "urgency_level": "HIGH",
          "recommendation": "STAT review",
          "generated_at": "2026-08-11T00:00:00Z"
        },
        "report_markdown": "# RADIOLOGY REPORT\nSTAT review",
        "is_valid_report": True
    }

    with patch("ml.inference.pipeline.run_pipeline", return_value=mock_pipeline_result):
        analyze_res = client.post(f"/api/v1/scans/{scan_id}/analyze")
        assert analyze_res.status_code == 200
        data = analyze_res.json()
        assert data["scan_id"] == scan_id
        assert data["status"] == "analyzed"
        assert data["is_valid_report"] is True
        assert data["decision_support"]["assessment"]["urgency_level"] == "HIGH"

def test_delete_scan_endpoint():
    upload_res = client.post(
        "/api/v1/scans/upload",
        files={"file": ("to_delete.dcm", b"mock bytes", "application/dicom")}
    )
    assert upload_res.status_code == 201
    scan_id = upload_res.json()["scan_id"]

    del_res = client.delete(f"/api/v1/scans/{scan_id}")
    assert del_res.status_code == 200
    assert del_res.json() == {"status": "deleted", "scan_id": scan_id}

    get_res = client.get(f"/api/v1/scans/{scan_id}")
    assert get_res.status_code == 404

