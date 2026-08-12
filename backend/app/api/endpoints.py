from fastapi import APIRouter, UploadFile, File, HTTPException
from backend.app.schemas.scan import ScanUploadResponse, ScanAnalysisResponse, ScanSummary
from backend.app.services.storage import StorageService
from typing import List, Optional
import os
import base64
import cv2
import numpy as np

router = APIRouter()
storage = StorageService()

def render_dicom_to_base64_png(file_path: str, window_center: float = 40.0, window_width: float = 80.0) -> Optional[str]:
    try:
        from ml.preprocessing.dicom_parser import read_dicom
        from ml.preprocessing.transforms import convert_to_hu, apply_window
        
        dcm = read_dicom(file_path)
        pixel_array = dcm.pixel_array
        
        # Ensure 2D slice for multi-frame or 3D/4D DICOM arrays
        while pixel_array.ndim > 2:
            if pixel_array.shape[0] > 1:
                pixel_array = pixel_array[pixel_array.shape[0] // 2]
            else:
                pixel_array = pixel_array[0]
                
        intercept_val = getattr(dcm, 'RescaleIntercept', 0.0)
        slope_val = getattr(dcm, 'RescaleSlope', 1.0)
        intercept = float(intercept_val[0] if isinstance(intercept_val, (list, tuple)) else intercept_val)
        slope = float(slope_val[0] if isinstance(slope_val, (list, tuple)) else slope_val)
        
        hu_img = convert_to_hu(pixel_array, intercept, slope)
        windowed = apply_window(hu_img, window_center, window_width)
        img_uint8 = (windowed * 255.0).astype(np.uint8)
        
        if img_uint8.ndim == 2:
            img_rgb = cv2.cvtColor(img_uint8, cv2.COLOR_GRAY2RGB)
        else:
            img_rgb = img_uint8
            
        _, buffer = cv2.imencode('.png', img_rgb)
        b64_str = base64.b64encode(buffer).decode('utf-8')
        return f"data:image/png;base64,{b64_str}"
    except Exception as e:
        print(f"Error rendering DICOM to PNG: {e}")
        return None

@router.post("/scans/upload", response_model=ScanUploadResponse, status_code=201)
async def upload_scan(file: UploadFile = File(...)):
    if not file.filename.endswith(('.dcm', '.DCM')):
        raise HTTPException(status_code=400, detail="Only DICOM (.dcm) files are supported.")
    
    content = await file.read()
    record = storage.save_scan(file.filename, content)
    
    img_b64 = render_dicom_to_base64_png(record["file_path"], 40.0, 80.0)
    
    return ScanUploadResponse(
        scan_id=record["scan_id"],
        filename=record["filename"],
        status=record["status"],
        uploaded_at=record["uploaded_at"],
        image_data_url=img_b64
    )

@router.post("/scans/load_demo", response_model=ScanUploadResponse, status_code=201)
def load_demo_scan():
    demo_file = os.path.join(os.getcwd(), "data", "demo_scans", "epidural_hematoma_ct.dcm")
    if not os.path.exists(demo_file):
        # Create on the fly if needed
        from scripts.create_demo_dataset import main as create_dataset
        create_dataset()
        
    with open(demo_file, "rb") as f:
        content = f.read()
        
    record = storage.save_scan("epidural_hematoma_ct.dcm", content)
    img_b64 = render_dicom_to_base64_png(record["file_path"], 40.0, 80.0)
    
    return ScanUploadResponse(
        scan_id=record["scan_id"],
        filename=record["filename"],
        status=record["status"],
        uploaded_at=record["uploaded_at"],
        image_data_url=img_b64
    )

@router.get("/scans/{scan_id}/image")
def get_scan_image(scan_id: str, preset: str = "brain"):
    record = storage.get_scan(scan_id)
    if not record:
        raise HTTPException(status_code=404, detail=f"Scan {scan_id} not found.")
    
    presets = {
        "brain": (40.0, 80.0),
        "subdural": (80.0, 200.0),
        "bone": (600.0, 2000.0)
    }
    wc, ww = presets.get(preset.lower(), (40.0, 80.0))
    img_b64 = render_dicom_to_base64_png(record["file_path"], wc, ww)
    
    return {
        "scan_id": scan_id,
        "preset": preset,
        "image_data_url": img_b64
    }

@router.post("/scans/{scan_id}/analyze", response_model=ScanAnalysisResponse)
def analyze_scan(scan_id: str):
    from ml.inference.pipeline import run_pipeline
    record = storage.get_scan(scan_id)
    if not record:
        raise HTTPException(status_code=404, detail=f"Scan {scan_id} not found.")
    
    file_path = record["file_path"]
    model_weights_path = os.path.join(os.getcwd(), "checkpoints", "best_model.pth")
    
    try:
        pipeline_output = run_pipeline(
            dicom_path=file_path,
            model_weights_path=model_weights_path,
            study_id=scan_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Inference pipeline error: {str(e)}")
        
    img_b64 = render_dicom_to_base64_png(file_path, 40.0, 80.0)
    pipeline_output["image_data_url"] = img_b64
    
    updated_record = storage.update_scan_analysis(scan_id, pipeline_output)
    
    return ScanAnalysisResponse(
        scan_id=scan_id,
        status="analyzed",
        decision_support=pipeline_output["decision_support"],
        radiology_report=pipeline_output["radiology_report"],
        report_markdown=pipeline_output["report_markdown"],
        is_valid_report=pipeline_output["is_valid_report"],
        analyzed_at=updated_record["analyzed_at"],
        image_data_url=img_b64,
        heatmap_data_url=pipeline_output.get("heatmap_data_url")
    )

@router.get("/scans/{scan_id}")
def get_scan_detail(scan_id: str):
    record = storage.get_scan(scan_id)
    if not record:
        raise HTTPException(status_code=404, detail=f"Scan {scan_id} not found.")
    return record

@router.delete("/scans/{scan_id}")
def delete_scan(scan_id: str):
    success = storage.delete_scan(scan_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Scan {scan_id} not found.")
    return {"status": "deleted", "scan_id": scan_id}

@router.get("/scans", response_model=List[ScanSummary])
def list_scans():
    records = storage.list_scans()
    summaries = []
    for r in records:
        sev = None
        urg = None
        if r.get("analysis"):
            sev = r["analysis"]["decision_support"]["assessment"]["severity_level"]
            urg = r["analysis"]["decision_support"]["assessment"]["urgency_level"]
        summaries.append(ScanSummary(
            scan_id=r["scan_id"],
            filename=r["filename"],
            status=r["status"],
            uploaded_at=r["uploaded_at"],
            severity_level=sev,
            urgency_level=urg
        ))
    return summaries

