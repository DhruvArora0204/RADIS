import os
import pandas as pd
import torch
from torch.utils.data import Dataset
from typing import Tuple

from ml.preprocessing.dicom_parser import read_dicom
from ml.preprocessing.transforms import convert_to_hu, get_multi_window_image, resize_image

class RSNADataset(Dataset):
    """
    PyTorch Dataset for the RSNA Intracranial Hemorrhage dataset.
    Loads DICOMs, applies preprocessing, and returns tensors.
    """
    def __init__(self, csv_path: str, img_dir: str, target_size: Tuple[int, int] = (256, 256)):
        """
        Args:
            csv_path: Path to the CSV file (e.g., train_split.csv) with columns for labels and SOPInstanceUID.
            img_dir: Directory containing the DICOM files (.dcm).
            target_size: Desired output image size (H, W).
        """
        self.df = pd.read_csv(csv_path)
        self.img_dir = img_dir
        self.target_size = target_size
        
        # Define the label columns we care about in the RSNA dataset
        self.label_cols = [
            'any', 
            'epidural', 
            'intraparenchymal', 
            'intraventricular', 
            'subarachnoid', 
            'subdural'
        ]

    def __len__(self):
        return len(self.df)

    def __getitem__(self, idx):
        row = self.df.iloc[idx]
        
        # ID is usually the SOPInstanceUID in RSNA
        sop_id = row['ID'].split('_')[1] if 'ID' in row else row['SOPInstanceUID']
        dcm_path = os.path.join(self.img_dir, f"ID_{sop_id}.dcm")
        
        # Read and preprocess
        try:
            dcm = read_dicom(dcm_path)
            pixel_array = dcm.pixel_array
            intercept = getattr(dcm, 'RescaleIntercept', 0.0)
            slope = getattr(dcm, 'RescaleSlope', 1.0)
            
            hu_image = convert_to_hu(pixel_array, intercept, slope)
            multi_window = get_multi_window_image(hu_image) # (3, H, W)
            resized = resize_image(multi_window, self.target_size)
            
            img_tensor = torch.from_numpy(resized).float()
            
        except Exception as e:
            # In case of missing file or bad DICOM, you might want to handle it
            # returning a zero tensor or skip in production.
            print(f"Error loading {dcm_path}: {e}")
            img_tensor = torch.zeros((3, self.target_size[0], self.target_size[1]), dtype=torch.float32)

        # Labels
        labels = row[self.label_cols].values.astype('float32')
        labels_tensor = torch.from_numpy(labels)

        return img_tensor, labels_tensor
