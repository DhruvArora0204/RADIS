import io
import pytest
import numpy as np
import pydicom
from pydicom.dataset import Dataset, FileMetaDataset
from pydicom.uid import ExplicitVRLittleEndian, SecondaryCaptureImageStorage, generate_uid
from fastapi.testclient import TestClient

from backend.app.main import app

client = TestClient(app)

def create_synthetic_dicom_bytes(rows=256, cols=256) -> bytes:
    """Helper to create a valid DICOM file in memory for end-to-end integration testing."""
    file_meta = FileMetaDataset()
    file_meta.MediaStorageSOPClassUID = SecondaryCaptureImageStorage
    file_meta.MediaStorageSOPInstanceUID = generate_uid()
    file_meta.TransferSyntaxUID = ExplicitVRLittleEndian

    ds = Dataset()
    ds.file_meta = file_meta
    ds.is_little_endian = True
    ds.is_implicit_VR = False

    ds.SOPClassUID = SecondaryCaptureImageStorage
    ds.SOPInstanceUID = file_meta.MediaStorageSOPInstanceUID
    ds.Modality = "CT"
    ds.PatientID = "E2E-PATIENT-001"

    ds.Rows = rows
    ds.Columns = cols
    ds.SamplesPerPixel = 1
    ds.PhotometricInterpretation = "MONOCHROME2"
    ds.BitsAllocated = 16
    ds.BitsStored = 12
    ds.HighBit = 11
    ds.PixelRepresentation = 0
    ds.RescaleIntercept = -1024.0
    ds.RescaleSlope = 1.0

    # Create dummy pixel array with CT-like brain values
    pixel_array = np.random.randint(900, 1100, (rows, cols), dtype=np.uint16)
    ds.PixelData = pixel_array.tobytes()

    buffer = io.BytesIO()
    pydicom.dcmwrite(buffer, ds, write_like_original=False)
    buffer.seek(0)
    return buffer.read()

def test_full_stack_end_to_end_flow():
    # 1. Verify Health Endpoint
    health_res = client.get("/health")
    assert health_res.status_code == 200

    # 2. Upload Synthetic DICOM
    dicom_bytes = create_synthetic_dicom_bytes()
    upload_res = client.post(
        "/api/v1/scans/upload",
        files={"file": ("e2e_scan.dcm", dicom_bytes, "application/dicom")}
    )
    assert upload_res.status_code == 201
    scan_id = upload_res.json()["scan_id"]
    assert scan_id.startswith("SCAN-")

    # 3. Analyze Scan via ML + Decision Support + Report Pipeline
    analyze_res = client.post(f"/api/v1/scans/{scan_id}/analyze")
    assert analyze_res.status_code == 200
    data = analyze_res.json()

    assert data["scan_id"] == scan_id
    assert data["status"] == "analyzed"
    assert data["is_valid_report"] is True
    assert "decision_support" in data
    assert "radiology_report" in data
    assert "# RADIOLOGY REPORT" in data["report_markdown"]

    # 4. Fetch Scan Detail
    detail_res = client.get(f"/api/v1/scans/{scan_id}")
    assert detail_res.status_code == 200
    assert detail_res.json()["status"] == "analyzed"

    # 5. Verify Frontend Static File Serving
    frontend_res = client.get("/")
    assert frontend_res.status_code == 200
    assert "RADIS Clinical AI Workstation" in frontend_res.text

    css_res = client.get("/styles.css")
    assert css_res.status_code == 200
    assert "app-header" in css_res.text

    js_res = client.get("/app.js")
    assert js_res.status_code == 200
    assert "initApp" in js_res.text

def test_multidimensional_dicom_upload_and_analyze():
    file_meta = FileMetaDataset()
    file_meta.MediaStorageSOPClassUID = SecondaryCaptureImageStorage
    file_meta.MediaStorageSOPInstanceUID = generate_uid()
    file_meta.TransferSyntaxUID = ExplicitVRLittleEndian

    ds = Dataset()
    ds.file_meta = file_meta
    ds.is_little_endian = True
    ds.is_implicit_VR = False
    ds.SOPClassUID = SecondaryCaptureImageStorage
    ds.SOPInstanceUID = file_meta.MediaStorageSOPInstanceUID
    ds.Modality = "CT"
    ds.Rows = 128
    ds.Columns = 128
    ds.NumberOfFrames = 1
    ds.SamplesPerPixel = 1
    ds.PhotometricInterpretation = "MONOCHROME2"
    ds.BitsAllocated = 16
    ds.BitsStored = 12
    ds.HighBit = 11
    ds.PixelRepresentation = 0
    ds.RescaleIntercept = -1024.0
    ds.RescaleSlope = 1.0

    # 3D pixel array (1, 128, 128)
    pixel_array = np.random.randint(900, 1100, (1, 128, 128), dtype=np.uint16)
    ds.PixelData = pixel_array.tobytes()

    buffer = io.BytesIO()
    pydicom.dcmwrite(buffer, ds, write_like_original=False)
    buffer.seek(0)

    upload_res = client.post(
        "/api/v1/scans/upload",
        files={"file": ("multidim_scan.dcm", buffer.read(), "application/dicom")}
    )
    assert upload_res.status_code == 201
    data = upload_res.json()
    assert data["image_data_url"] is not None

    scan_id = data["scan_id"]
    analyze_res = client.post(f"/api/v1/scans/{scan_id}/analyze")
    assert analyze_res.status_code == 200
    assert analyze_res.json()["image_data_url"] is not None
