import numpy as np
import torch
from sklearn.metrics import roc_auc_score, average_precision_score, f1_score
from typing import Dict

def compute_metrics(y_true: np.ndarray, y_pred_probs: np.ndarray, threshold: float = 0.5) -> Dict[str, float]:
    """
    Computes classification metrics for multi-label prediction.
    
    Args:
        y_true: True binary labels (N_samples, N_classes)
        y_pred_probs: Predicted probabilities (after sigmoid) (N_samples, N_classes)
        threshold: Threshold for converting probabilities to binary predictions
        
    Returns:
        A dictionary containing average AUROC, AUPRC, and F1 across all classes.
    """
    y_pred_bin = (y_pred_probs >= threshold).astype(float)
    
    metrics = {}
    
    # We use macro average for multi-label
    try:
        metrics['macro_auroc'] = roc_auc_score(y_true, y_pred_probs, average='macro')
    except ValueError:
        # Happens if a class has only one label in the batch/dataset
        metrics['macro_auroc'] = float('nan')
        
    try:
        metrics['macro_auprc'] = average_precision_score(y_true, y_pred_probs, average='macro')
    except ValueError:
        metrics['macro_auprc'] = float('nan')
        
    metrics['macro_f1'] = f1_score(y_true, y_pred_bin, average='macro', zero_division=0)
    
    return metrics

if __name__ == "__main__":
    # Test block
    y_t = np.array([[1, 0], [0, 1], [1, 1], [0, 0]])
    y_p = np.array([[0.9, 0.1], [0.2, 0.8], [0.7, 0.9], [0.1, 0.3]])
    m = compute_metrics(y_t, y_p)
    print(m)
