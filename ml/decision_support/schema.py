from pydantic import BaseModel, Field
from typing import List, Optional, Tuple

class Finding(BaseModel):
    label: str = Field(..., description="The type of pathology detected (e.g., epidural, subdural)")
    probability: float = Field(..., description="The confidence score from the model [0, 1]")
    bounding_box: Optional[Tuple[int, int, int, int]] = Field(None, description="The bounding box (x, y, w, h) of the finding")

class ClinicalAssessment(BaseModel):
    urgency_level: str = Field(..., description="Urgency of the finding: HIGH, MEDIUM, LOW")
    severity_level: str = Field(..., description="Severity of the finding: HIGH, MEDIUM, LOW")
    workflow_recommendation: str = Field(..., description="Recommendation for clinical workflow")

class DecisionSupportOutput(BaseModel):
    findings: List[Finding] = Field(default_factory=list, description="List of individual findings")
    assessment: ClinicalAssessment = Field(..., description="Overall clinical assessment")
    timestamp: str = Field(..., description="ISO 8601 timestamp of when the assessment was generated")
