from typing import List
from datetime import datetime, timezone
from .schema import Finding, ClinicalAssessment, DecisionSupportOutput

class ClinicalRuleEngine:
    def __init__(self):
        # Define high-urgency pathologies (often require immediate surgical intervention or close monitoring)
        self.high_urgency_labels = {'epidural', 'subarachnoid', 'subdural'}
        
    def evaluate(self, findings: List[Finding]) -> DecisionSupportOutput:
        """
        Evaluates a list of findings to produce a clinical assessment.
        """
        if not findings:
            assessment = ClinicalAssessment(
                urgency_level="LOW",
                severity_level="LOW",
                workflow_recommendation="Routine review"
            )
            return DecisionSupportOutput(
                findings=[],
                assessment=assessment,
                timestamp=datetime.now(timezone.utc).isoformat()
            )

        highest_urgency = "LOW"
        highest_severity = "LOW"
        
        for finding in findings:
            # Urgency Logic
            if finding.label in self.high_urgency_labels:
                highest_urgency = "HIGH"
            elif highest_urgency != "HIGH" and finding.probability >= 0.8:
                highest_urgency = "MEDIUM"
                
            # Severity Logic
            if finding.probability >= 0.9:
                highest_severity = "HIGH"
            elif highest_severity != "HIGH" and finding.probability >= 0.7:
                highest_severity = "MEDIUM"
                
            # Additional proxy for severity: bounding box size (if available)
            if finding.bounding_box:
                x, y, w, h = finding.bounding_box
                area = w * h
                # Arbitrary threshold for MVP: if area is large (> 10% of 256x256 image = 6500)
                if area > 6500 and highest_severity != "HIGH":
                    highest_severity = "HIGH"
                    
        # Workflow Recommendation Logic
        if highest_urgency == "HIGH" or highest_severity == "HIGH":
            recommendation = "STAT radiology review recommended (High Severity/Urgency detected)."
        elif highest_urgency == "MEDIUM" or highest_severity == "MEDIUM":
            recommendation = "Priority review recommended."
        else:
            recommendation = "Routine review."
            
        assessment = ClinicalAssessment(
            urgency_level=highest_urgency,
            severity_level=highest_severity,
            workflow_recommendation=recommendation
        )
        
        return DecisionSupportOutput(
            findings=findings,
            assessment=assessment,
            timestamp=datetime.now(timezone.utc).isoformat()
        )
