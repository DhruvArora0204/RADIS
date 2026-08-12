import torch
import torch.nn.functional as F
import numpy as np
import cv2

class GradCAM:
    """
    Grad-CAM implementation for PyTorch models.
    """
    def __init__(self, model, target_layer):
        self.model = model
        self.target_layer = target_layer
        self.gradients = None
        self.activations = None
        
        # Hook the target layer
        self.target_layer.register_forward_hook(self.save_activation)
        self.target_layer.register_full_backward_hook(self.save_gradient)
        
    def save_activation(self, module, input, output):
        self.activations = output
        
    def save_gradient(self, module, grad_input, grad_output):
        # grad_output is a tuple
        self.gradients = grad_output[0]
        
    def generate_heatmap(self, input_tensor, target_class_idx):
        """
        Generates a Grad-CAM heatmap for a given input tensor and target class.
        Args:
            input_tensor: Tensor of shape (1, C, H, W)
            target_class_idx: Index of the class to explain
        Returns:
            heatmap: Numpy array of shape (H, W) normalized between 0 and 1.
        """
        # Ensure model is in eval mode but requires grad for input
        self.model.eval()
        
        # Forward pass
        output = self.model(input_tensor)
        
        if target_class_idx is None:
            target_class_idx = torch.argmax(output).item()
            
        # Target for backprop
        self.model.zero_grad()
        target = output[0, target_class_idx]
        target.backward()
        
        # Get gradients and activations
        gradients = self.gradients.cpu().data.numpy()[0] # (Channels, H_feat, W_feat)
        activations = self.activations.cpu().data.numpy()[0] # (Channels, H_feat, W_feat)
        
        # Global Average Pooling of gradients to get weights
        weights = np.mean(gradients, axis=(1, 2)) # (Channels,)
        
        # Weighted sum of activations
        cam = np.zeros(activations.shape[1:], dtype=np.float32)
        for i, w in enumerate(weights):
            cam += w * activations[i]
            
        # ReLU on CAM (only positive influences)
        cam = np.maximum(cam, 0)
        
        # Resize CAM to match input image size (H, W)
        input_size = (input_tensor.shape[3], input_tensor.shape[2]) # (W, H)
        cam = cv2.resize(cam, input_size)
        
        # Normalize
        cam_min, cam_max = cam.min(), cam.max()
        if cam_max - cam_min > 0:
            cam = (cam - cam_min) / (cam_max - cam_min)
            
        return cam

def overlay_heatmap(image_np, heatmap, colormap=cv2.COLORMAP_JET, alpha=0.5):
    """
    Overlays a heatmap onto an image.
    Args:
        image_np: Base image (H, W, 3) normalized [0, 1]
        heatmap: Heatmap (H, W) normalized [0, 1]
    """
    # Convert heatmap to RGB heatmap
    heatmap_colored = cv2.applyColorMap(np.uint8(255 * heatmap), colormap)
    heatmap_colored = cv2.cvtColor(heatmap_colored, cv2.COLOR_BGR2RGB)
    heatmap_colored = heatmap_colored.astype(np.float32) / 255.0
    
    # Blend
    overlay = (1.0 - alpha) * image_np + alpha * heatmap_colored
    overlay = np.clip(overlay, 0, 1)
    
    return overlay

def extract_bounding_box(heatmap, threshold=0.6):
    """
    Extracts a bounding box from the heatmap based on a threshold.
    Returns (x, y, w, h) or None if no region found.
    """
    # Threshold heatmap
    binary = (heatmap >= threshold).astype(np.uint8) * 255
    
    # Find contours
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    if not contours:
        return None
        
    # Get largest contour
    largest_contour = max(contours, key=cv2.contourArea)
    x, y, w, h = cv2.boundingRect(largest_contour)
    
    # Return bounding box if the area is meaningful (e.g., > 10 pixels)
    if w * h > 10:
        return (x, y, w, h)
    return None
