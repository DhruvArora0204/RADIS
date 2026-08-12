# DATASET PLAN

## Dataset Comparison

| Dataset | Modality | Pathology | Labels | Segmentation | Reports | Access |
|---|---|---|---|---|---|---|
| **RSNA Intracranial Hemorrhage (Kaggle)** | CT (Brain) | Hemorrhage (5 subtypes) | Yes (Image-level) | No | No | Public (Kaggle/AWS) |
| **CQ500 (via PhysioNet / Qure.ai)** | CT (Brain) | Hemorrhage, Midline Shift, Mass Effect | Yes (Study-level) | No (BHX provides BBoxes) | Yes (Some NLP derived) | Public |
| **CT-ORG (TCIA)** | CT (Various) | Organ Segmentation (Brain included) | N/A | Yes | No | Public |

## Recommended Dataset Strategy
For the RADIS MVP, we will primarily utilize the **RSNA Intracranial Hemorrhage Dataset** for training the baseline slice-level classifier, combined with the **CQ500 Dataset** (specifically utilizing the BHX bounding box extensions available on PhysioNet) for evaluating study-level findings, midline shift, mass effect, and localization.

1. **Primary Focus**: Hemorrhage detection (RSNA).
2. **Secondary Focus**: Localization using BHX (CQ500 extension).

## Data Leakage Prevention (CRITICAL)
- **Rule**: Data split MUST be performed at the **Patient or Study ID level**, never at the individual slice level.
- Slices from the same patient will be grouped.
- Train (70%), Validation (15%), Test (15%) splits will be pre-computed and saved as static CSV files before any processing to guarantee strict separation.

## Preprocessing
- DICOMs will be read and converted to Hounsfield Units (HU).
- Windowing will be applied (Brain: W:80 L:40, Subdural: W:130-300 L:50-100, Bone: W:2800 L:600).
- Data will be resized to a uniform spatial resolution.
