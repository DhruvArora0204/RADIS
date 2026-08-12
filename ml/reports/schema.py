from pydantic import BaseModel, Field
from typing import List, Optional

class RadiologyReport(BaseModel):
    study_id: str = Field(..., description="Unique study identifier")
    patient_id: Optional[str] = Field("ANONYMOUS", description="Patient ID")
    clinical_history: str = Field(..., description="Clinical indication / history")
    technique: str = Field(..., description="Scan protocol description")
    findings_section: List[str] = Field(..., description="Detailed findings bullet points")
    impression_section: List[str] = Field(..., description="Summary conclusions & diagnostic impressions")
    severity_level: str = Field(..., description="HIGH, MEDIUM, or LOW severity")
    urgency_level: str = Field(..., description="HIGH, MEDIUM, or LOW urgency")
    recommendation: str = Field(..., description="Actionable clinical workflow recommendation")
    generated_at: str = Field(..., description="ISO timestamp of report generation")

    def to_markdown(self) -> str:
        """Converts report object to a cleanly formatted Markdown document."""
        md = f"# RADIOLOGY REPORT\n\n"
        md += f"**Study ID:** {self.study_id} | **Patient ID:** {self.patient_id}\n"
        md += f"**Date/Time:** {self.generated_at}\n\n"
        md += f"### CLINICAL HISTORY\n{self.clinical_history}\n\n"
        md += f"### TECHNIQUE\n{self.technique}\n\n"
        md += f"### FINDINGS\n"
        for item in self.findings_section:
            md += f"- {item}\n"
        md += f"\n### IMPRESSION\n"
        for i, item in enumerate(self.impression_section, 1):
            md += f"{i}. {item}\n"
        md += f"\n---\n"
        md += f"**Urgency:** {self.urgency_level} | **Severity:** {self.severity_level}\n"
        md += f"**Workflow Recommendation:** {self.recommendation}\n"
        return md
