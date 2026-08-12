import pydicom
import os
from typing import Dict, Any, Optional

def read_dicom(path: str) -> pydicom.dataset.FileDataset:
    """
    Reads a DICOM file from a given path.
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"DICOM file not found at {path}")
    return pydicom.dcmread(path)

def validate_dicom(dcm: pydicom.dataset.FileDataset) -> bool:
    """
    Validates if the given DICOM dataset is suitable for the RADIS MVP.
    Specifically, we check if it is a CT scan. Further checks for 'Head'
    and 'Non-contrast' can be added depending on the exact dataset tags.
    """
    try:
        modality = getattr(dcm, 'Modality', '')
        if modality != 'CT':
            return False
        
        # Optional: check body part examined if available
        body_part = getattr(dcm, 'BodyPartExamined', '').upper()
        if body_part and 'HEAD' not in body_part and 'BRAIN' not in body_part:
            # We don't strictly fail here since some datasets omit it,
            # but ideally it should be Head/Brain.
            pass
            
        return True
    except Exception:
        return False

def extract_metadata(dcm: pydicom.dataset.FileDataset) -> Dict[str, Any]:
    """
    Extracts relevant metadata from a DICOM dataset.
    Returns a dictionary of metadata attributes.
    """
    metadata = {
        'PatientID': getattr(dcm, 'PatientID', None),
        'StudyInstanceUID': getattr(dcm, 'StudyInstanceUID', None),
        'SeriesInstanceUID': getattr(dcm, 'SeriesInstanceUID', None),
        'SOPInstanceUID': getattr(dcm, 'SOPInstanceUID', None),
        'Modality': getattr(dcm, 'Modality', None),
        'BodyPartExamined': getattr(dcm, 'BodyPartExamined', None),
        'SliceThickness': getattr(dcm, 'SliceThickness', None),
        'PixelSpacing': getattr(dcm, 'PixelSpacing', None),
        'RescaleIntercept': getattr(dcm, 'RescaleIntercept', 0.0),
        'RescaleSlope': getattr(dcm, 'RescaleSlope', 1.0),
        'Rows': getattr(dcm, 'Rows', None),
        'Columns': getattr(dcm, 'Columns', None)
    }
    return metadata
