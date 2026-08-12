# EVALUATION PLAN

## AI Evaluation

### Dataset Split
- Data will be split by **Patient ID / Study ID**.
- Split ratio: 70% Train, 15% Validation, 15% Test.

### Metrics
1. **Classification (Hemorrhage Detection)**
   - Primary: AUROC (Area Under the Receiver Operating Characteristic curve)
   - Secondary: Sensitivity (Recall), Specificity, F1-Score, AUPRC
2. **Localization**
   - Intersection over Union (IoU) for bounding boxes.
3. **Calibration**
   - Expected Calibration Error (ECE) to ensure confidence scores align with actual probabilities.

### Model Comparison
- **Baseline**: 2D ResNet-50 trained from scratch on raw slices.
- **Iterative Improvements**: Fine-tuned weights, addition of windowing channels, 2.5D or 3D architectures.

## System Evaluation

### Inference Performance
- **Target Inference Time**: < 2 minutes per study (100-300 slices).
- **Target End-to-End Latency**: < 3 minutes from upload completion to report generation.

### Resource Utilization
- Track GPU Memory usage during inference to ensure it can run on a standard consumer/workstation GPU (e.g., 8GB - 16GB VRAM) for the MVP.
- Track CPU and RAM usage during DICOM preprocessing (HU conversion and windowing can be memory intensive).
