import os
import json
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

UPLOADS_DIR = os.path.join(os.getcwd(), "data", "uploads")
METADATA_FILE = os.path.join(os.getcwd(), "data", "scans_metadata.json")

class StorageService:
    def __init__(self):
        os.makedirs(UPLOADS_DIR, exist_ok=True)
        os.makedirs(os.path.dirname(METADATA_FILE), exist_ok=True)
        if not os.path.exists(METADATA_FILE):
            with open(METADATA_FILE, "w") as f:
                json.dump({}, f)

    def _load_metadata(self) -> Dict[str, Any]:
        try:
            with open(METADATA_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return {}

    def _save_metadata(self, data: Dict[str, Any]):
        with open(METADATA_FILE, "w") as f:
            json.dump(data, f, indent=2)

    def save_scan(self, filename: str, content: bytes) -> Dict[str, Any]:
        scan_id = f"SCAN-{uuid.uuid4().hex[:8].upper()}"
        file_path = os.path.join(UPLOADS_DIR, f"{scan_id}_{filename}")
        
        with open(file_path, "wb") as f:
            f.write(content)
            
        record = {
            "scan_id": scan_id,
            "filename": filename,
            "file_path": file_path,
            "status": "uploaded",
            "uploaded_at": datetime.now(timezone.utc).isoformat(),
            "analysis": None
        }
        
        meta = self._load_metadata()
        meta[scan_id] = record
        self._save_metadata(meta)
        
        return record

    def get_scan(self, scan_id: str) -> Optional[Dict[str, Any]]:
        meta = self._load_metadata()
        return meta.get(scan_id)

    def list_scans(self) -> List[Dict[str, Any]]:
        meta = self._load_metadata()
        return list(meta.values())

    def update_scan_analysis(self, scan_id: str, analysis_result: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        meta = self._load_metadata()
        if scan_id not in meta:
            return None
        
        meta[scan_id]["status"] = "analyzed"
        meta[scan_id]["analysis"] = analysis_result
        meta[scan_id]["analyzed_at"] = datetime.now(timezone.utc).isoformat()
        
        self._save_metadata(meta)
        return meta[scan_id]

    def delete_scan(self, scan_id: str) -> bool:
        meta = self._load_metadata()
        if scan_id not in meta:
            return False
        
        record = meta.pop(scan_id)
        self._save_metadata(meta)
        
        file_path = record.get("file_path")
        if file_path and os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception:
                pass
        return True
