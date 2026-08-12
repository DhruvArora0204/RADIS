# MODEL PLAN

## Baseline Model
The initial baseline will be a simple 2D convolutional neural network (e.g., ResNet-50) trained on individual 2D slices to classify the presence or absence of hemorrhage.

## Candidate Architectures
1. **Classification (Slice-level)**: ResNet-50 / DenseNet-121.
2. **Classification (Study-level)**: 2.5D approaches (using adjacent slices as channels) or a 3D CNN / CNN-RNN (LSTM over slices).
3. **Localization**: YOLO (for bounding boxes via BHX dataset) or Grad-CAM on the classification model for explainable attention maps.

## Explainability
- **Grad-CAM**: Will be implemented on the baseline classifier to generate heatmaps highlighting the region contributing most to the "hemorrhage present" prediction.
- **Confidence Scores**: Raw softmax probabilities will be calibrated.

## Confidence & Uncertainty
- A high-confidence threshold (e.g., 0.85) will be required to display a positive AI finding automatically.
- Scores between 0.4 and 0.85 will trigger an "Uncertainty / Manual Review Recommended" state.
- Scores below 0.4 will be considered negative.

## Evaluation Metrics
- **Classification**: AUROC, AUPRC, Sensitivity, Specificity, F1-Score.
- **Localization**: Intersection over Union (IoU) if bounding boxes are used.
