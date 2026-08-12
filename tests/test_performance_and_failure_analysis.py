import pytest
import numpy as np
import io
import pydicom
from pydicom.dataset import Dataset, FileMetaDataset
from pydicom.uid import ExplicitVRLittleEndian, SecondaryCaptureImageStorage, generate_uid
from fastapi.testclient import TestClient

from ml.evaluation.eval_metrics import calculate_multilabel_metrics, benchmark_inference_latency
from backend.app.main import app

client = TestClient(app)

def test_calculate_multilabel_metrics():
    y_true = np.array([
        [1, 1, 0, 0, 0, 0],
        [0, 0, 1, 0, 0, 0],
        [0, 0, 0, 0, 0, 0],
        [1, 0, 0, 0, 1, 0]
    ])
    y_pred = np.array([
        [0.9, 0.85, 0.1, 0.05, 0.1, 0.05],
        [0.1, 0.05, 0.95, 0.1, 0.05, 0.1],
        [0.05, 0.05, 0.1, 0.05, 0.1, 0.05],
        [0.85, 0.1, 0.05, 0.05, 0.88, 0.05]
    ])
    
    metrics = calculate_multilabel_metrics(y_true, y_pred)
    assert "macro_summary" in metrics
    assert "epidural" in metrics
    assert metrics["macro_summary"]["macro_roc_auc"] >= 0.5
    assert metrics["epidural"]["f1_score"] == 1.0

def test_corrupted_dicom_upload_resilience():
    corrupted_bytes = b"CORRUPTED_HEADER_DATA_12345"
    response = client.post(
        "/api/v1/scans/upload",
        files={"file": ("corrupted.dcm", corrupted_bytes, "application/dicom")}
    )
    assert response.status_code == 201 # Saved as upload
    scan_id = response.json()["scan_id"]
    
    # Analyzing corrupted DICOM should return a handled 500 error instead of uncaught crash
    analyze_res = client.post(f"/api/v1/scans/{scan_id}/analyze")
    assert analyze_res.status_code == 500
    assert "Inference pipeline error" in analyze_res.json()["detail"]

def test_zero_pixel_array_dicom_resilience():
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
    ds.SamplesPerPixel = 1
    ds.PhotometricInterpretation = "MONOCHROME2"
    ds.BitsAllocated = 16
    ds.BitsStored = 12
    ds.HighBit = 11
    ds.PixelRepresentation = 0
    ds.RescaleIntercept = 0.0
    ds.RescaleSlope = 1.0
    
    # All zeros
    ds.PixelData = np.zeros((128, 128), dtype=np.uint16).tobytes()

    buffer = io.BytesIO()
    pydicom.dcmwrite(buffer, ds, write_like_original=False)
    buffer.seek(0)
    zero_bytes = buffer.read()

    upload_res = client.post(
        "/api/v1/scans/upload",
        files={"file": ("zero_scan.dcm", zero_bytes, "application/dicom")}
    )
    assert upload_res.status_code == 201
    scan_id = upload_res.json()["scan_id"]

    analyze_res = client.post(f"/api/v1/scans/{scan_id}/analyze")
    assert analyze_res.status_code == 200
    assert analyze_res.json()["is_valid_report"] is True
