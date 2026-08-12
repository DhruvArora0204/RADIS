import pytest
from ml.decision_support.schema import Finding
from ml.decision_support.rule_engine import ClinicalRuleEngine

def test_empty_findings():
    engine = ClinicalRuleEngine()
    result = engine.evaluate([])
    
    assert result.assessment.urgency_level == "LOW"
    assert result.assessment.severity_level == "LOW"
    assert "Routine review" in result.assessment.workflow_recommendation

def test_high_urgency_pathology():
    engine = ClinicalRuleEngine()
    findings = [
        Finding(label="epidural", probability=0.6, bounding_box=None)
    ]
    result = engine.evaluate(findings)
    
    assert result.assessment.urgency_level == "HIGH"
    assert result.assessment.severity_level == "LOW" # Since prob < 0.7
    assert "STAT" in result.assessment.workflow_recommendation
    
def test_high_severity_pathology():
    engine = ClinicalRuleEngine()
    findings = [
        Finding(label="intraparenchymal", probability=0.95, bounding_box=None)
    ]
    result = engine.evaluate(findings)
    
    assert result.assessment.urgency_level == "MEDIUM" # High prob triggers MEDIUM urgency if not high-urgency label
    assert result.assessment.severity_level == "HIGH" # prob >= 0.9
    assert "STAT" in result.assessment.workflow_recommendation
    
def test_large_bounding_box():
    engine = ClinicalRuleEngine()
    findings = [
        Finding(label="intraparenchymal", probability=0.8, bounding_box=(0, 0, 100, 100)) # Area = 10000 > 6500
    ]
    result = engine.evaluate(findings)
    
    assert result.assessment.urgency_level == "MEDIUM"
    assert result.assessment.severity_level == "HIGH" # Triggered by bounding box
    
def test_medium_severity():
    engine = ClinicalRuleEngine()
    findings = [
        Finding(label="intraparenchymal", probability=0.75, bounding_box=(0, 0, 50, 50)) # Area = 2500 < 6500
    ]
    result = engine.evaluate(findings)
    
    assert result.assessment.urgency_level == "LOW"
    assert result.assessment.severity_level == "MEDIUM" # Triggered by prob >= 0.7
    assert "Priority" in result.assessment.workflow_recommendation
