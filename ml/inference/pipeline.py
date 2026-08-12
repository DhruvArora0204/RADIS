import os
import torch
import numpy as np
import json

from ml.preprocessing.dicom_parser import read_dicom
from ml.preprocessing.transforms import convert_to_hu, get_multi_window_image, resize_image
from ml.models.baseline_cnn import BaselineResNet
from ml.explainability.gradcam import GradCAM, extract_bounding_box
from ml.decision_support.schema import Finding
from ml.decision_support.rule_engine import ClinicalRuleEngine
from ml.reports.generator import ReportGenerator
from ml.reports.validator import ReportValidator

LABELS = [
    'any', 
    'epidural', 
    'intraparenchymal', 
    'intraventricular', 
    'subarachnoid', 
    'subdural'
]

def run_pipeline(dicom_path: str, model_weights_path: str, target_size=(256, 256), prob_threshold=0.5, study_id: str = "STD-001"):
    """
    End-to-end inference pipeline:
    1. Preprocess DICOM
    2. Model Inference
    3. Explainability (Grad-CAM bounding boxes for positive classes)
    4. Clinical Rule Engine
    5. Report Generator & Validator
    """
    
    # 1. Parse and Preprocess
    dcm = read_dicom(dicom_path)
    pixel_array = dcm.pixel_array
    
    # Ensure 2D slice for multi-frame or 3D/4D DICOM arrays
    while pixel_array.ndim > 2:
        if pixel_array.shape[0] > 1:
            pixel_array = pixel_array[pixel_array.shape[0] // 2]
        else:
            pixel_array = pixel_array[0]

    intercept_val = getattr(dcm, 'RescaleIntercept', 0.0)
    slope_val = getattr(dcm, 'RescaleSlope', 1.0)
    intercept = float(intercept_val[0] if isinstance(intercept_val, (list, tuple)) else intercept_val)
    slope = float(slope_val[0] if isinstance(slope_val, (list, tuple)) else slope_val)
    
    hu_image = convert_to_hu(pixel_array, intercept, slope)
    multi_window = get_multi_window_image(hu_image) # (3, H, W)
    resized_np = resize_image(multi_window, target_size)
    
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
        
    # 3. Generate Findings with Bounding Boxes & Grad-CAM Heatmap Data URL
    findings = []
    target_layer = model.base_model.layer4[-1]
    gradcam = GradCAM(model, target_layer)
    
    combined_heatmap = np.zeros(target_size, dtype=np.float32)
    has_positive = False

    for i in range(1, 6):
        prob = float(probs[i])
        if prob >= prob_threshold:
            heatmap = gradcam.generate_heatmap(input_tensor, target_class_idx=i)
            combined_heatmap = np.maximum(combined_heatmap, heatmap)
            has_positive = True
            bbox = extract_bounding_box(heatmap, threshold=0.7)
            
            finding = Finding(
                label=LABELS[i],
                probability=prob,
                bounding_box=bbox
            )
            findings.append(finding)
            
    any_prob = float(probs[0])
    if any_prob >= prob_threshold:
        if not has_positive:
            combined_heatmap = gradcam.generate_heatmap(input_tensor, target_class_idx=0)
        findings.append(Finding(
            label=LABELS[0],
            probability=any_prob,
            bounding_box=None
        ))

    heatmap_data_url = None
    if has_positive or any_prob >= prob_threshold:
        import cv2
        import base64
        heatmap_uint8 = (combined_heatmap * 255.0).astype(np.uint8)
        color_heatmap = cv2.applyColorMap(heatmap_uint8, cv2.COLORMAP_JET)
        mask = (heatmap_uint8 > 25).astype(np.uint8) * 255
        b, g, r = cv2.split(color_heatmap)
        rgba = cv2.merge([b, g, r, mask])
        _, buffer = cv2.imencode('.png', rgba)
        b64_str = base64.b64encode(buffer).decode('utf-8')
        heatmap_data_url = f"data:image/png;base64,{b64_str}"

    # 4. Clinical Rule Engine
    engine = ClinicalRuleEngine()
    assessment = engine.evaluate(findings)
    
    # 5. Report Generation & Validation
    report_gen = ReportGenerator()
    report = report_gen.generate(assessment, study_id=study_id)
    is_valid = ReportValidator.validate(report)
    
    return {
        "decision_support": assessment.model_dump(),
        "radiology_report": report.model_dump(),
        "report_markdown": report.to_markdown(),
        "is_valid_report": is_valid,
        "heatmap_data_url": heatmap_data_url
    }

if __name__ == "__main__":
    pass

