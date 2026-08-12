from ml.reports.schema import RadiologyReport

class ReportValidator:
    @staticmethod
    def validate(report: RadiologyReport) -> bool:
        """Validates that a RadiologyReport contains all essential non-empty fields."""
        if not report.study_id or not report.study_id.strip():
            return False
        if not report.findings_section or len(report.findings_section) == 0:
            return False
        if not report.impression_section or len(report.impression_section) == 0:
            return False
        if report.severity_level not in {"HIGH", "MEDIUM", "LOW"}:
            return False
        if report.urgency_level not in {"HIGH", "MEDIUM", "LOW"}:
            return False
        return True
