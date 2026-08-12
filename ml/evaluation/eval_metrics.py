import time
import numpy as np
from typing import Dict, Any, List
from sklearn.metrics import roc_auc_score, f1_score, precision_score, recall_score, confusion_matrix

LABELS = [
    'any', 
    'epidural', 
    'intraparenchymal', 
    'intraventricular', 
    'subarachnoid', 
    'subdural'
]

def calculate_multilabel_metrics(y_true: np.ndarray, y_pred_probs: np.ndarray, threshold: float = 0.5) -> Dict[str, Any]:
    """
    Computes per-class and macro-averaged metrics for multi-label hemorrhage detection.
    y_true: Binary matrix of shape (N, 6)
    y_pred_probs: Predicted probabilities matrix of shape (N, 6)
    """
    y_pred_bin = (y_pred_probs >= threshold).astype(int)
    results = {}
    
    macro_auc = []
    macro_f1 = []
    
    for i, label in enumerate(LABELS):
        # Calculate per-class metrics
        try:
            auc = float(roc_auc_score(y_true[:, i], y_pred_probs[:, i]))
            if np.isnan(auc):
                auc = 0.5
        except Exception:
            auc = 0.5
            
        f1 = float(f1_score(y_true[:, i], y_pred_bin[:, i], zero_division=0))
        prec = float(precision_score(y_true[:, i], y_pred_bin[:, i], zero_division=0))
        rec = float(recall_score(y_true[:, i], y_pred_bin[:, i], zero_division=0))
        
        macro_auc.append(auc)
        macro_f1.append(f1)
        
        results[label] = {
            "roc_auc": round(auc, 4),
            "f1_score": round(f1, 4),
            "precision": round(prec, 4),
            "sensitivity_recall": round(rec, 4)
        }
        
    results["macro_summary"] = {
        "macro_roc_auc": round(float(np.mean(macro_auc)), 4),
        "macro_f1": round(float(np.mean(macro_f1)), 4)
    }
    
    return results

def benchmark_inference_latency(pipeline_fn, sample_dicom_path: str, weights_path: str, num_runs: int = 5) -> Dict[str, Any]:
    """
    Measures execution latency of the end-to-end inference pipeline.
    """
    latencies = []
    for _ in range(num_runs):
        start = time.perf_counter()
        _ = pipeline_fn(sample_dicom_path, weights_path)
        elapsed = (time.perf_counter() - start) * 1000.0 # ms
        latencies.append(elapsed)
        
    return {
        "num_runs": num_runs,
        "mean_latency_ms": round(float(np.mean(latencies)), 2),
        "std_latency_ms": round(float(np.std(latencies)), 2),
        "p95_latency_ms": round(float(np.percentile(latencies, 95)), 2),
        "min_latency_ms": round(float(np.min(latencies)), 2),
        "max_latency_ms": round(float(np.max(latencies)), 2)
    }
