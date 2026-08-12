import os
import torch
import cv2
import matplotlib.pyplot as plt
import numpy as np

from ml.preprocessing.dicom_parser import read_dicom
from ml.preprocessing.transforms import convert_to_hu, get_multi_window_image, resize_image
from ml.models.baseline_cnn import BaselineResNet
from ml.explainability.gradcam import GradCAM, overlay_heatmap, extract_bounding_box

# We define the labels according to the RSNA dataset standard we established
LABELS = [
    'any', 
    'epidural', 
    'intraparenchymal', 
    'intraventricular', 
    'subarachnoid', 
    'subdural'
]

def visualize_prediction(dicom_path: str, model_weights_path: str, output_path: str, target_size=(256, 256)):
    """
    End-to-end inference script that takes a DICOM file, runs it through the model,
    generates a Grad-CAM heatmap, extracts a bounding box, and saves the visualization.
    """
    
    # 1. Parse and Preprocess
    dcm = read_dicom(dicom_path)
    pixel_array = dcm.pixel_array
    intercept = getattr(dcm, 'RescaleIntercept', 0.0)
    slope = getattr(dcm, 'RescaleSlope', 1.0)
    
    hu_image = convert_to_hu(pixel_array, intercept, slope)
    multi_window = get_multi_window_image(hu_image) # (3, H, W)
    resized_np = resize_image(multi_window, target_size)
    
    # Normalize for display (just take the brain window channel 0 for grayscale display)
    display_image = resized_np[0] # Brain window (H, W)
    display_image_rgb = np.stack((display_image,)*3, axis=-1) # (H, W, 3)
    
    # 2. Model Inference
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model = BaselineResNet(num_classes=6, pretrained=False)
    
    if os.path.exists(model_weights_path):
        model.load_state_dict(torch.load(model_weights_path, map_location=device))
    else:
        print(f"Warning: Model weights not found at {model_weights_path}. Using untrained model.")
        
    model.to(device)
    model.eval()
    
    input_tensor = torch.from_numpy(resized_np).float().unsqueeze(0).to(device) # (1, 3, H, W)
    
    with torch.no_grad():
        outputs = model(input_tensor)
        probs = torch.sigmoid(outputs).cpu().numpy()[0]
        
    print("Predictions:")
    for label, prob in zip(LABELS, probs):
        print(f"  {label}: {prob:.4f}")
        
    # 3. Grad-CAM for the highest probability class
    top_class_idx = np.argmax(probs)
    print(f"Generating Grad-CAM for target class: {LABELS[top_class_idx]}")
    
    # The last convolutional layer in ResNet50 is layer4
    target_layer = model.base_model.layer4[-1]
    
    gradcam = GradCAM(model, target_layer)
    heatmap = gradcam.generate_heatmap(input_tensor, target_class_idx=top_class_idx)
    
    # 4. Overlay and Bounding Box
    overlay = overlay_heatmap(display_image_rgb, heatmap)
    bbox = extract_bounding_box(heatmap, threshold=0.7)
    
    if bbox:
        x, y, w, h = bbox
        # Draw rectangle (Red)
        cv2.rectangle(overlay, (x, y), (x+w, y+h), (1.0, 0.0, 0.0), 2)
        
    # 5. Save Visualization
    fig, ax = plt.subplots(1, 2, figsize=(12, 6))
    
    ax[0].imshow(display_image, cmap='gray')
    ax[0].set_title("Original Brain Window")
    ax[0].axis('off')
    
    ax[1].imshow(overlay)
    ax[1].set_title(f"Grad-CAM (Target: {LABELS[top_class_idx]})")
    ax[1].axis('off')
    
    plt.tight_layout()
    plt.savefig(output_path)
    print(f"Saved visualization to {output_path}")

if __name__ == "__main__":
    # Example usage:
    # visualize_prediction("data/sample.dcm", "checkpoints/best_model.pth", "output_vis.png")
    pass
