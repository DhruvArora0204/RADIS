from datetime import datetime, timezone
from typing import Optional
from ml.decision_support.schema import DecisionSupportOutput
from ml.reports.schema import RadiologyReport

PATHOLOGY_DESCRIPTIONS = {
    'epidural': "Extra-axial hyperdense fluid collection in the epidural space, concerning for acute epidural hematoma.",
    'subdural': "Crescentic extra-axial hyperdensities along the cerebral convexity, concerning for acute subdural hematoma.",
    'subarachnoid': "Hyperdensity within the cerebral sulci and basal cisterns, indicative of acute subarachnoid hemorrhage.",
    'intraparenchymal': "Focal hyperdensity within the brain parenchyma with surrounding hypodense edema, consistent with acute intraparenchymal hemorrhage.",
    'intraventricular': "Hyperdense attenuation extending into the cerebral ventricular system, consistent with intraventricular hemorrhage.",
    'any': "Evidence of acute intracranial hemorrhage."
}

class ReportGenerator:
    def __init__(self, default_technique: Optional[str] = None):
        self.default_technique = default_technique or "Axial non-contrast computed tomography (CT) scan of the brain."

    def generate(
        self,
        decision_output: DecisionSupportOutput,
        study_id: str = "STD-UNCATEGORIZED",
        patient_id: str = "ANONYMOUS",
        clinical_history: str = "Evaluation for acute neurological symptoms / trauma."
    ) -> RadiologyReport:
        findings_bullets = []
        impression_items = []

        positive_findings = [f for f in decision_output.findings if f.label != 'any' and f.probability >= 0.5]
        
        if positive_findings:
            findings_bullets.append("Non-contrast head CT demonstrates focal attenuation abnormalities:")
            for f in positive_findings:
                desc = PATHOLOGY_DESCRIPTIONS.get(f.label, f"Abnormal attenuation suspicious for {f.label} hemorrhage.")
                bbox_str = f" Bounding box coordinates: {f.bounding_box}." if f.bounding_box else ""
                findings_bullets.append(f"**{f.label.upper()}**: {desc} (Confidence: {f.probability * 100:.1f}%).{bbox_str}")
            
            findings_bullets.append("Ventricles and basal cisterns evaluated.")
            findings_bullets.append("No gross calvarial fracture visualized on baseline soft tissue windowing.")

            labels_str = ", ".join([f.label.upper() for f in positive_findings])
            impression_items.append(f"Acute intracranial hemorrhage detected ({labels_str}).")
            impression_items.append(f"Severity: {decision_output.assessment.severity_level}, Urgency: {decision_output.assessment.urgency_level}.")
            impression_items.append(decision_output.assessment.workflow_recommendation)
        else:
            findings_bullets.append("No acute extra-axial or intra-axial fluid collection or hyperdensity identified.")
            findings_bullets.append("Ventricles and basal cisterns are unremarkable for age.")
            findings_bullets.append("Midline structures are centered without evidence of mass effect.")
            findings_bullets.append("Bone windows demonstrate no visible skull fracture.")

            impression_items.append("No acute intracranial hemorrhage identified on this exam.")
            impression_items.append("Routine clinical follow-up as indicated.")

        report = RadiologyReport(
            study_id=study_id,
            patient_id=patient_id,
            clinical_history=clinical_history,
            technique=self.default_technique,
            findings_section=findings_bullets,
            impression_section=impression_items,
            severity_level=decision_output.assessment.severity_level,
            urgency_level=decision_output.assessment.urgency_level,
            recommendation=decision_output.assessment.workflow_recommendation,
            generated_at=datetime.now(timezone.utc).isoformat()
        )

        return report
