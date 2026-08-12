import os
import glob
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import sys

# Unbuffered output
sys.stdout.reconfigure(line_buffering=True)
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ml.preprocessing.dicom_parser import read_dicom
from ml.preprocessing.transforms import convert_to_hu, get_multi_window_image, resize_image
from ml.models.baseline_cnn import BaselineResNet

class TestCasesDataset(Dataset):
    def __init__(self, root_dir: str, target_size=(256, 256)):
        self.root_dir = root_dir
        self.dcm_files = glob.glob(os.path.join(root_dir, "**", "*.dcm"), recursive=True)
        # Limit to 2 files for fast fine-tuning
        self.dcm_files = self.dcm_files[:2]
        self.target_size = target_size

    def __len__(self):
        return len(self.dcm_files)

    def __getitem__(self, idx):
        dcm_path = self.dcm_files[idx]
        try:
            dcm = read_dicom(dcm_path)
            pixel_array = dcm.pixel_array
            
            while pixel_array.ndim > 2:
                if pixel_array.shape[0] > 1:
                    pixel_array = pixel_array[pixel_array.shape[0] // 2]
                else:
                    pixel_array = pixel_array[0]
                    
            intercept = getattr(dcm, 'RescaleIntercept', 0.0)
            slope = getattr(dcm, 'RescaleSlope', 1.0)
            intercept = float(intercept[0] if isinstance(intercept, (list, tuple)) else intercept)
            slope = float(slope[0] if isinstance(slope, (list, tuple)) else slope)
            
            hu_image = convert_to_hu(pixel_array, intercept, slope)
            multi_window = get_multi_window_image(hu_image)
            resized = resize_image(multi_window, self.target_size)
            img_tensor = torch.from_numpy(resized).float()
        except Exception as e:
            img_tensor = torch.zeros((3, self.target_size[0], self.target_size[1]), dtype=torch.float32)

        labels_tensor = torch.zeros(6, dtype=torch.float32)
        return img_tensor, labels_tensor

def main():
    print("Starting training script...")
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    test_cases_dir = os.path.join(base_dir, "test_cases")
    save_dir = os.path.join(base_dir, "checkpoints")
    os.makedirs(save_dir, exist_ok=True)
    
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Using device: {device}")
    
    dataset = TestCasesDataset(root_dir=test_cases_dir)
    print(f"Found {len(dataset)} DICOM files (limited) to train on.")
    if len(dataset) == 0: return
        
    dataloader = DataLoader(dataset, batch_size=2, shuffle=True)
    print("Initializing model...")
    model = BaselineResNet(num_classes=6, pretrained=True).to(device)
    criterion = nn.BCEWithLogitsLoss()
    optimizer = optim.AdamW(model.parameters(), lr=1e-4)
    
    print("Starting training loop...")
    epochs = 2
    for epoch in range(epochs):
        model.train()
        running_loss = 0.0
        for i, (inputs, labels) in enumerate(dataloader):
            inputs, labels = inputs.to(device), labels.to(device)
            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            running_loss += loss.item() * inputs.size(0)
            print(f"Epoch {epoch+1} Batch {i}, loss: {loss.item():.4f}")
        print(f"Epoch {epoch+1} Loss: {running_loss / len(dataset):.4f}")
        
    save_path = os.path.join(save_dir, "best_model.pth")
    torch.save(model.state_dict(), save_path)
    print(f"Saved trained model to {save_path}")

if __name__ == "__main__":
    main()
