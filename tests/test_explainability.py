import torch
import numpy as np
from ml.models.baseline_cnn import BaselineResNet
from ml.explainability.gradcam import GradCAM, extract_bounding_box

def test_gradcam_heatmap_shape():
    # Setup model and dummy input
    model = BaselineResNet(num_classes=6, pretrained=False)
    target_layer = model.base_model.layer4[-1]
    
    # 1 batch, 3 channels, 256x256
    dummy_input = torch.randn(1, 3, 256, 256)
    
    gradcam = GradCAM(model, target_layer)
    heatmap = gradcam.generate_heatmap(dummy_input, target_class_idx=0)
    
    # Heatmap should be 2D and match spatial dims of input
    assert heatmap.shape == (256, 256)
    # Should be normalized
    assert heatmap.min() >= 0.0
    assert heatmap.max() <= 1.0

def test_extract_bounding_box():
    # Create a synthetic heatmap (256x256) with a "hot" region
    heatmap = np.zeros((256, 256), dtype=np.float32)
    # Add a hot square in the middle
    heatmap[100:150, 100:150] = 0.9
    
    bbox = extract_bounding_box(heatmap, threshold=0.7)
    
    # Should detect the square
    assert bbox is not None
    x, y, w, h = bbox
    assert x == 100
    assert y == 100
    assert w == 50
    assert h == 50
    
    # Test empty bbox (no region above threshold)
    heatmap_cold = np.zeros((256, 256), dtype=np.float32)
    bbox_cold = extract_bounding_box(heatmap_cold, threshold=0.7)
    assert bbox_cold is None
