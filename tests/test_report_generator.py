import pytest
from ml.decision_support.schema import Finding
from ml.decision_support.rule_engine import ClinicalRuleEngine
from ml.reports.generator import ReportGenerator
from ml.reports.validator import ReportValidator

def test_report_generation_negative_scan():
    engine = ClinicalRuleEngine()
    assessment = engine.evaluate([])
    
    generator = ReportGenerator()
    report = generator.generate(assessment, study_id="TEST-001")
    
    assert report.study_id == "TEST-001"
    assert "No acute extra-axial or intra-axial fluid collection" in report.findings_section[0]
    assert "No acute intracranial hemorrhage identified" in report.impression_section[0]
    assert ReportValidator.validate(report) is True

def test_report_generation_positive_scan():
    engine = ClinicalRuleEngine()
    findings = [
        Finding(label="epidural", probability=0.92, bounding_box=(10, 20, 50, 60))
    ]
    assessment = engine.evaluate(findings)
    
    generator = ReportGenerator()
    report = generator.generate(assessment, study_id="TEST-002")
    
    assert report.study_id == "TEST-002"
    assert report.urgency_level == "HIGH"
    assert report.severity_level == "HIGH"
    assert any("EPIDURAL" in f for f in report.findings_section)
    assert any("Acute intracranial hemorrhage detected" in imp for imp in report.impression_section)
    
    md = report.to_markdown()
    assert "# RADIOLOGY REPORT" in md
    assert "**Urgency:** HIGH" in md
    assert ReportValidator.validate(report) is True
