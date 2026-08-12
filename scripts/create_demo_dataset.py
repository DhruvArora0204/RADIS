import os
import numpy as np
import pydicom
from pydicom.dataset import Dataset, FileMetaDataset
from pydicom.uid import ExplicitVRLittleEndian, SecondaryCaptureImageStorage, generate_uid

DEMO_DIR = os.path.join(os.getcwd(), "data", "demo_scans")

def create_dicom_file(filename: str, patient_name: str, pathology: str = "normal"):
    os.makedirs(DEMO_DIR, exist_ok=True)
    file_path = os.path.join(DEMO_DIR, filename)

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
    ds.PatientName = patient_name
    ds.PatientID = f"DEMO-{np.random.randint(1000, 9999)}"
    ds.StudyDescription = f"Brain CT - {pathology.upper()}"

    ds.Rows = 256
    ds.Columns = 256
    ds.SamplesPerPixel = 1
    ds.PhotometricInterpretation = "MONOCHROME2"
    ds.BitsAllocated = 16
    ds.BitsStored = 12
    ds.HighBit = 11
    ds.PixelRepresentation = 0
    ds.RescaleIntercept = -1024.0
    ds.RescaleSlope = 1.0

    # Base Brain CT Pixel Array (HU 40 brain tissue = 1064 in stored uint16 with intercept -1024)
    arr = np.full((256, 256), 1064, dtype=np.uint16)
    
    # Background air (-1000 HU = 24 uint16)
    y, x = np.ogrid[:256, :256]
    mask_bg = ((x - 128)**2 + (y - 128)**2) > 110**2
    arr[mask_bg] = 24

    # Skull bone (1000 HU = 2024 uint16)
    mask_skull = (((x - 128)**2 + (y - 128)**2) <= 110**2) & (((x - 128)**2 + (y - 128)**2) >= 98**2)
    arr[mask_skull] = 2024

    # Add simulated pathology hyperdensities (80 HU = 1104 uint16)
    if pathology == "epidural":
        mask_hem = (((x - 180)**2 + (y - 128)**2) <= 25**2) & (((x - 128)**2 + (y - 128)**2) < 98**2)
        arr[mask_hem] = 1104
    elif pathology == "subdural":
        mask_hem = (((x - 80)**2 + (y - 100)**2) <= 30**2) & (((x - 128)**2 + (y - 128)**2) < 98**2)
        arr[mask_hem] = 1104
    elif pathology == "subarachnoid":
        mask_hem = (((x - 128)**2 + (y - 160)**2) <= 20**2)
        arr[mask_hem] = 1104

    ds.PixelData = arr.tobytes()
    pydicom.dcmwrite(file_path, ds, write_like_original=False)
    print(f"Created demo scan: {file_path}")

def main():
    print("Generating demo DICOM CT scans in data/demo_scans/...")
    create_dicom_file("normal_brain_ct.dcm", "Demo Normal", "normal")
    create_dicom_file("epidural_hematoma_ct.dcm", "Demo Epidural", "epidural")
    create_dicom_file("subdural_hematoma_ct.dcm", "Demo Subdural", "subdural")
    create_dicom_file("subarachnoid_hemorrhage_ct.dcm", "Demo Subarachnoid", "subarachnoid")
    print("Demo dataset ready!")

if __name__ == "__main__":
    main()
