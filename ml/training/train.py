import os
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from tqdm import tqdm
import numpy as np

from ml.models.baseline_cnn import BaselineResNet
from ml.datasets.rsna_dataset import RSNADataset
from ml.evaluation.metrics import compute_metrics

def train_one_epoch(model, dataloader, criterion, optimizer, device):
    model.train()
    running_loss = 0.0
    
    for inputs, labels in tqdm(dataloader, desc="Training"):
        inputs = inputs.to(device)
        labels = labels.to(device)
        
        optimizer.zero_grad()
        outputs = model(inputs)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()
        
        running_loss += loss.item() * inputs.size(0)
        
    return running_loss / len(dataloader.dataset)

def validate(model, dataloader, criterion, device):
    model.eval()
    running_loss = 0.0
    
    all_labels = []
    all_preds = []
    
    with torch.no_grad():
        for inputs, labels in tqdm(dataloader, desc="Validating"):
            inputs = inputs.to(device)
            labels = labels.to(device)
            
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            
            running_loss += loss.item() * inputs.size(0)
            
            probs = torch.sigmoid(outputs)
            all_labels.append(labels.cpu().numpy())
            all_preds.append(probs.cpu().numpy())
            
    epoch_loss = running_loss / len(dataloader.dataset)
    
    all_labels = np.vstack(all_labels)
    all_preds = np.vstack(all_preds)
    
    metrics = compute_metrics(all_labels, all_preds)
    
    return epoch_loss, metrics

def run_training(train_csv: str, val_csv: str, img_dir: str, epochs: int = 10, batch_size: int = 32, lr: float = 1e-4, save_dir: str = "checkpoints"):
    os.makedirs(save_dir, exist_ok=True)
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Using device: {device}")
    
    # Dataset and DataLoader
    train_dataset = RSNADataset(csv_path=train_csv, img_dir=img_dir)
    val_dataset = RSNADataset(csv_path=val_csv, img_dir=img_dir)
    
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True, num_workers=4)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False, num_workers=4)
    
    # Model
    model = BaselineResNet(num_classes=6, pretrained=True).to(device)
    
    # Loss and Optimizer
    criterion = nn.BCEWithLogitsLoss()
    optimizer = optim.AdamW(model.parameters(), lr=lr)
    
    best_val_loss = float('inf')
    
    for epoch in range(epochs):
        print(f"\\nEpoch {epoch+1}/{epochs}")
        train_loss = train_one_epoch(model, train_loader, criterion, optimizer, device)
        val_loss, metrics = validate(model, val_loader, criterion, device)
        
        print(f"Train Loss: {train_loss:.4f} | Val Loss: {val_loss:.4f}")
        print(f"Val AUROC: {metrics['macro_auroc']:.4f} | Val AUPRC: {metrics['macro_auprc']:.4f}")
        
        if val_loss < best_val_loss:
            best_val_loss = val_loss
            save_path = os.path.join(save_dir, "best_model.pth")
            torch.save(model.state_dict(), save_path)
            print(f"Saved new best model to {save_path}")

if __name__ == "__main__":
    # Example execution
    # run_training('data/splits/train_split.csv', 'data/splits/val_split.csv', 'data/images/')
    pass
