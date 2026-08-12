import torch
import numpy as np
from ml.models.baseline_cnn import BaselineResNet
from ml.evaluation.metrics import compute_metrics

def test_model_output_shape():
    model = BaselineResNet(num_classes=6, pretrained=False)
    # Batch size 2, 3 channels, 256x256 image
    dummy_input = torch.randn(2, 3, 256, 256)
    output = model(dummy_input)
    
    # Should output logits for 6 classes for each item in the batch
    assert output.shape == (2, 6)
    
def test_compute_metrics():
    # 4 samples, 2 classes
    y_true = np.array([
        [1, 0],
        [0, 1],
        [1, 1],
        [0, 0]
    ])
    
    # Probabilities
    y_pred_probs = np.array([
        [0.9, 0.1],  # True pos, True neg
        [0.2, 0.8],  # True neg, True pos
        [0.7, 0.9],  # True pos, True pos
        [0.1, 0.3]   # True neg, True neg
    ])
    
    # All predictions are perfectly correct if threshold is 0.5
    metrics = compute_metrics(y_true, y_pred_probs, threshold=0.5)
    
    # AUROC should be 1.0 for both classes, so macro avg is 1.0
    assert np.isclose(metrics['macro_auroc'], 1.0)
    assert np.isclose(metrics['macro_f1'], 1.0)
