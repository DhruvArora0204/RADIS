from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class ScanUploadResponse(BaseModel):
    scan_id: str = Field(..., description="Unique ID generated for the scan")
    filename: str = Field(..., description="Original filename of uploaded DICOM")
    status: str = Field("uploaded", description="Current status of the scan (uploaded, analyzed, failed)")
    uploaded_at: str = Field(..., description="Timestamp when scan was uploaded")
    image_data_url: Optional[str] = Field(None, description="Base64 PNG image URL of DICOM slice")

class ScanAnalysisResponse(BaseModel):
    scan_id: str
    status: str
    decision_support: Dict[str, Any]
    radiology_report: Dict[str, Any]
    report_markdown: str
    is_valid_report: bool
    analyzed_at: str
    image_data_url: Optional[str] = None
    heatmap_data_url: Optional[str] = None

class ScanSummary(BaseModel):
    scan_id: str
    filename: str
    status: str
    uploaded_at: str
    severity_level: Optional[str] = None
    urgency_level: Optional[str] = None
