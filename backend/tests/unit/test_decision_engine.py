import pytest
from app.schemas.examination import (
    DetectorResult,
    DetectorStatus,
    EvidenceStrength,
    TechnicalAssessment,
    EvidenceRegion,
)
from app.analysis.fusion.evidence_family import EvidenceFamilyManager
from app.analysis.fusion.decision_engine import ForensicDecisionEngine


def test_strong_tampering_copy_move_decision():
    reg = EvidenceRegion(x=50, y=50, width=80, height=80, confidence=0.92, detector="copy_move_forgery_detection")
    res = DetectorResult(
        detector_name="copy_move_forgery_detection",
        detector_version="2.0.0",
        status=DetectorStatus.POSITIVE.value,
        score=0.88,
        confidence=0.90,
        evidence_strength=EvidenceStrength.STRONG.value,
        affected_regions=[reg],
    )

    families = EvidenceFamilyManager.group_detector_results([res])
    char = {"has_camera_exif": False, "image_class": "PHOTOGRAPH"}

    decision = ForensicDecisionEngine.evaluate([res], families, char)

    assert decision.final_assessment == TechnicalAssessment.LIKELY_TAMPERED.value
    assert decision.human_review_required is True
    assert len(decision.decisive_observations) == 1
    assert decision.evidence_strength in [EvidenceStrength.STRONG.value, EvidenceStrength.VERY_STRONG.value]
    assert "Copy-Move" in decision.decisive_observations[0].finding


def test_authentic_camera_photo_decision():
    # Detectors report normal/negative statistics on clean camera capture
    detectors = [
        DetectorResult(detector_name="error_level_analysis", detector_version="2.0.0", status=DetectorStatus.NEGATIVE.value, score=0.05),
        DetectorResult(detector_name="noise_residual_analysis", detector_version="2.0.0", status=DetectorStatus.NEGATIVE.value, score=0.05),
        DetectorResult(detector_name="copy_move_forgery_detection", detector_version="2.0.0", status=DetectorStatus.NEGATIVE.value, score=0.02),
        DetectorResult(detector_name="image_splicing_detector", detector_version="2.0.0", status=DetectorStatus.NEGATIVE.value, score=0.04),
        DetectorResult(detector_name="ai_generative_classifier", detector_version="2.0.0", status=DetectorStatus.NEGATIVE.value, score=0.08),
    ]

    families = EvidenceFamilyManager.group_detector_results(detectors)
    char = {"has_camera_exif": True, "camera_make": "Canon", "camera_model": "EOS R5", "image_class": "PHOTOGRAPH"}

    decision = ForensicDecisionEngine.evaluate(detectors, families, char)

    assert decision.final_assessment == TechnicalAssessment.LIKELY_AUTHENTIC.value
    assert decision.human_review_required is True
    assert len(decision.decisive_observations) == 0
    assert decision.evidence_strength == EvidenceStrength.MODERATE.value


def test_weak_single_detector_does_not_force_tampered():
    # Only a single weak residual anomaly without any corroboration
    detectors = [
        DetectorResult(detector_name="noise_residual_analysis", detector_version="2.0.0", status=DetectorStatus.POSITIVE.value, score=0.55, confidence=0.60),
        DetectorResult(detector_name="copy_move_forgery_detection", detector_version="2.0.0", status=DetectorStatus.NEGATIVE.value, score=0.02),
        DetectorResult(detector_name="image_splicing_detector", detector_version="2.0.0", status=DetectorStatus.NEGATIVE.value, score=0.03),
    ]

    families = EvidenceFamilyManager.group_detector_results(detectors)
    char = {"has_camera_exif": False, "image_class": "PHOTOGRAPH"}

    decision = ForensicDecisionEngine.evaluate(detectors, families, char)

    # Must NOT produce LIKELY_TAMPERED from a single uncorroborated weak residual signal
    assert decision.final_assessment == TechnicalAssessment.INCONCLUSIVE.value
    assert decision.human_review_required is True


def test_conflicting_evidence_produces_inconclusive_or_caution():
    # Positive manipulation but authentic camera provenance intact
    detectors = [
        DetectorResult(detector_name="copy_move_forgery_detection", detector_version="2.0.0", status=DetectorStatus.POSITIVE.value, score=0.85, confidence=0.88),
        DetectorResult(detector_name="metadata_examination", detector_version="2.0.0", status=DetectorStatus.NEGATIVE.value, score=0.05),
    ]
    families = EvidenceFamilyManager.group_detector_results(detectors)
    char = {"has_camera_exif": True, "image_class": "PHOTOGRAPH"}

    decision = ForensicDecisionEngine.evaluate(detectors, families, char)

    # Should flag contradictory observation
    assert len(decision.contradictory_observations) > 0
    assert decision.human_review_required is True

