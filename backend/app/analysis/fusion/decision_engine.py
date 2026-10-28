from typing import List, Dict, Any, Optional
from app.schemas.examination import (
    DetectorResult,
    DetectorStatus,
    EvidenceStrength,
    TechnicalAssessment,
    DecisiveObservation,
    DecisionEngineOutput,
    EvidenceFamilySummary,
)
from app.analysis.fusion.calibration import ForensicCalibrator


class ForensicDecisionEngine:
    """
    Forensic Decision Engine & Calibrated Multi-Evidence Fusion.
    Converts normalized detector results into a defensible technical assessment.
    Conforms to the forensic doctrine: 'The tool screens. The expert decides.'
    """
    RULES_VERSION = "2026.2-v2"
    DEFAULT_PROFILE = "production-v2"

    @classmethod
    def evaluate(
        cls,
        detector_results: List[DetectorResult],
        evidence_families: Dict[str, EvidenceFamilySummary],
        image_characterization: Dict[str, Any],
        threshold_profile: str = DEFAULT_PROFILE,
    ) -> DecisionEngineOutput:
        """
        Executes calibrated multi-evidence evaluation:
        1. Identifies decisive observations (high-confidence primary manipulation detectors).
        2. Identifies supporting observations (secondary or contextual anomalies).
        3. Identifies contradictory observations (conflicting evidence between families).
        4. Identifies inconclusive and not applicable tests.
        5. Computes independent evidence-family consensus to determine final technical assessment.
        """
        decisive_observations: List[DecisiveObservation] = []
        supporting_observations: List[str] = []
        contradictory_observations: List[str] = []
        inconclusive_tests: List[str] = []
        not_applicable_tests: List[str] = []

        # Triage individual detector outputs
        for res in detector_results:
            d_name = res.detector_name
            if res.status == DetectorStatus.NOT_APPLICABLE.value:
                not_applicable_tests.append(d_name)
            elif res.status == DetectorStatus.INCONCLUSIVE.value:
                inconclusive_tests.append(d_name)
            elif res.status == DetectorStatus.POSITIVE.value:
                # Check for Decisive primary indicators
                if d_name == "copy_move_forgery_detection" and res.score >= 0.70 and res.confidence >= 0.75:
                    reg = res.affected_regions[0] if res.affected_regions else None
                    decisive_observations.append(
                        DecisiveObservation(
                            detector=d_name,
                            finding=f"Copy-Move Cloning: Spatially separated duplicated regions confirmed ({len(res.affected_regions)} cluster/regions).",
                            confidence=res.confidence,
                            region=reg,
                        )
                    )
                elif d_name == "image_splicing_detector" and res.score >= 0.60 and res.confidence >= 0.70:
                    reg = res.affected_regions[0] if res.affected_regions else None
                    decisive_observations.append(
                        DecisiveObservation(
                            detector=d_name,
                            finding=f"Image Splicing: Multi-source composite boundary and regional statistical mismatch detected ({len(res.affected_regions)} anomalous regions).",
                            confidence=res.confidence,
                            region=reg,
                        )
                    )
                elif d_name == "ai_generative_classifier" and res.score >= 0.75 and res.confidence >= 0.75:
                    decisive_observations.append(
                        DecisiveObservation(
                            detector=d_name,
                            finding=f"Generative AI Synthesis: Synthetic likelihood index {round(res.score * 100, 1)}% exceeds physical optical camera threshold.",
                            confidence=res.confidence,
                        )
                    )
                elif d_name == "c2pa_provenance" and "AI" in res.technical_reason:
                    decisive_observations.append(
                        DecisiveObservation(
                            detector=d_name,
                            finding="C2PA Provenance Manifest explicitly declares Generative AI synthesis.",
                            confidence=res.confidence,
                        )
                    )
                elif d_name == "document_typography_and_alignment" and res.score >= 0.70:
                    reg = res.affected_regions[0] if res.affected_regions else None
                    decisive_observations.append(
                        DecisiveObservation(
                            detector=d_name,
                            finding=f"Document Typography Discrepancy: Character baseline and edge alignment anomalies detected.",
                            confidence=res.confidence,
                            region=reg,
                        )
                    )
                else:
                    # Supporting observation
                    reason_clean = res.technical_reason or f"{d_name} reported statistical anomaly."
                    supporting_observations.append(f"{d_name}: {reason_clean}")

        # Check for Contradictory evidence
        manip_fam = evidence_families.get("MANIPULATION")
        prov_fam = evidence_families.get("PROVENANCE")
        resid_fam = evidence_families.get("RESIDUAL")

        if manip_fam and manip_fam.status == "SUPPORTING_TAMPERING":
            if prov_fam and prov_fam.status == "SUPPORTING_AUTHENTIC":
                contradictory_observations.append(
                    "Manipulation detector flagged localized edits while file retains camera EXIF hardware metadata."
                )
        if resid_fam and resid_fam.status == "SUPPORTING_TAMPERING":
            if not manip_fam or manip_fam.status != "SUPPORTING_TAMPERING":
                contradictory_observations.append(
                    "High-pass residual variance detected, but without spatial copy-move or structural splicing corroboration."
                )

        # Count independent evidence families supporting tampering
        supporting_tamper_families = [
            f_name for f_name, f_sum in evidence_families.items()
            if f_sum.status == "SUPPORTING_TAMPERING"
        ]

        # Multi-family evidence fusion decision rules
        has_decisive_tamper = len(decisive_observations) >= 1
        num_tamper_families = len(supporting_tamper_families)

        if has_decisive_tamper or num_tamper_families >= 2:
            final_assessment = TechnicalAssessment.LIKELY_TAMPERED.value
            # Compute confidence from decisive and supporting families
            max_conf = max([d.confidence for d in decisive_observations]) if decisive_observations else 0.82
            decision_confidence = round(min(0.96, max_conf + (0.04 * (num_tamper_families - 1))), 2)

            if num_tamper_families >= 3 and has_decisive_tamper:
                evidence_strength = EvidenceStrength.VERY_STRONG.value
            elif has_decisive_tamper or num_tamper_families >= 2:
                evidence_strength = EvidenceStrength.STRONG.value
            else:
                evidence_strength = EvidenceStrength.MODERATE.value

            decision_rationale = (
                f"Multi-evidence correlation identified {len(decisive_observations)} decisive finding(s) "
                f"across {num_tamper_families} independent evidence family/families ({', '.join(supporting_tamper_families)}). "
                "Technical indicators exhibit statistically significant divergence from an unmanipulated baseline."
            )

        elif (
            image_characterization.get("has_camera_exif")
            and num_tamper_families == 0
            and len(supporting_observations) == 0
            and len(inconclusive_tests) <= 3
        ):
            # Cautious authentic assessment
            final_assessment = TechnicalAssessment.LIKELY_AUTHENTIC.value
            decision_confidence = 0.84
            evidence_strength = EvidenceStrength.MODERATE.value
            decision_rationale = (
                "Camera hardware provenance metadata is intact and no statistical manipulation "
                "or recompression indicators were detected across applicable forensic screening tests. "
                "Per forensic standards, absence of detected anomalies supports authenticity but does not constitute absolute proof."
            )

        elif num_tamper_families == 1 and not has_decisive_tamper:
            # Single weak family (e.g. only residual or only ELA) without corroboration MUST NOT trigger LIKELY_TAMPERED!
            final_assessment = TechnicalAssessment.INCONCLUSIVE.value
            decision_confidence = 0.52
            evidence_strength = EvidenceStrength.LOW.value
            decision_rationale = (
                f"Isolated statistical anomaly observed in '{supporting_tamper_families[0]}' family, "
                "but lacked independent corroboration from manipulation, compression, or provenance families. "
                "Inconclusive screening finding; manual microscopic examination required."
            )

        else:
            final_assessment = TechnicalAssessment.INCONCLUSIVE.value
            decision_confidence = 0.50
            evidence_strength = EvidenceStrength.NONE.value
            decision_rationale = (
                f"Screening produced non-decisive or mixed observations across tests "
                f"({len(inconclusive_tests)} inconclusive, {len(not_applicable_tests)} not applicable). "
                "No decisive indicators of tampering or confirmed provenance chains were established."
            )

        return DecisionEngineOutput(
            final_assessment=final_assessment,
            decision_confidence=decision_confidence,
            evidence_strength=evidence_strength,
            human_review_required=True,  # Crucial doctrine: Tool screens. Expert decides.
            decisive_observations=decisive_observations,
            supporting_observations=supporting_observations,
            contradictory_observations=contradictory_observations,
            inconclusive_tests=inconclusive_tests,
            not_applicable_tests=not_applicable_tests,
            decision_rationale=decision_rationale,
            evidence_families=evidence_families,
            rules_version=cls.RULES_VERSION,
            threshold_profile=threshold_profile,
        )

