import pytest
from app.schemas.examination import (
    DetectorResult,
    DetectorStatus,
    EvidenceStrength,
    EvidenceRegion,
    EvidenceFamilyType,
)
from app.analysis.fusion.evidence_family import EvidenceFamilyManager


def test_detector_result_schema():
    reg = EvidenceRegion(x=10, y=20, width=50, height=50, confidence=0.88, detector="copymove", label="Cloned Region")
    res = DetectorResult(
        detector_name="copy_move_forgery_detection",
        detector_version="2.0.0",
        status=DetectorStatus.POSITIVE.value,
        score=0.88,
        confidence=0.85,
        evidence_strength=EvidenceStrength.STRONG.value,
        applicable=True,
        technical_reason="Duplicate region confirmed.",
        affected_regions=[reg],
        execution_time_ms=120.5,
    )

    assert res.status == "POSITIVE"
    assert res.score == 0.88
    assert res.evidence_strength == "STRONG"
    assert len(res.affected_regions) == 1
    assert res.affected_regions[0].label == "Cloned Region"


def test_evidence_family_grouping_and_discounting():
    # Simulate multiple correlated residual detectors triggering
    res1 = DetectorResult(
        detector_name="noise_residual_analysis",
        detector_version="2.0.0",
        status=DetectorStatus.POSITIVE.value,
        score=0.70,
        confidence=0.75,
    )
    res2 = DetectorResult(
        detector_name="srm_wavelet_analysis",
        detector_version="2.0.0",
        status=DetectorStatus.POSITIVE.value,
        score=0.65,
        confidence=0.70,
    )
    res3 = DetectorResult(
        detector_name="fourier_spectral_analysis",
        detector_version="2.0.0",
        status=DetectorStatus.POSITIVE.value,
        score=0.60,
        confidence=0.70,
    )

    families = EvidenceFamilyManager.group_detector_results([res1, res2, res3])
    assert EvidenceFamilyType.RESIDUAL.value in families
    resid_fam = families[EvidenceFamilyType.RESIDUAL.value]

    # Verify discounting: aggregate score must not be 0.70 + 0.65 + 0.60 = 1.95!
    # Diminishing returns formula: max + 0.25*second + 0.10*third
    assert resid_fam.aggregate_score <= 1.0
    assert resid_fam.aggregate_score < (0.70 + 0.65 + 0.60)
    assert resid_fam.status == "SUPPORTING_TAMPERING"
    assert len(resid_fam.member_detectors) == 3

