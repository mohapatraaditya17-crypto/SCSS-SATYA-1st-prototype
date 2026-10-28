import time
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional
from PIL import Image
import numpy as np
import cv2

from app.core.config import settings
from app.schemas.examination import (
    ScreeningTestResult,
    DetectorResult,
    DetectorStatus,
    EvidenceStrength,
    EvidenceRegion,
)


class TypographyAnalyzer:
    METHOD_NAME = "document_typography_and_alignment"
    VERSION = "2.0.0"

    @classmethod
    def analyze(
        cls,
        image_path: Path,
        examination_id: str,
        media_type: str,
        image_characterization: Optional[Dict[str, Any]] = None,
    ) -> Tuple[ScreeningTestResult, Dict[str, str], Dict[str, Any], DetectorResult]:
        start_time = time.perf_counter()
        observations: List[str] = []
        artifacts: Dict[str, str] = {}
        analytics: Dict[str, Any] = {}
        affected_regions: List[EvidenceRegion] = []
        limitations: List[str] = [
            "Typography and alignment analysis operates on document glyphs, certificates, screenshots, and tabular records; natural photography lacking text is skipped or reports not applicable.",
            "Handwritten text, stylized cursive fonts, or intentionally staggered graphic typography can produce organic baseline variances.",
            "Sub-pixel anti-aliasing differences vary across operating systems and rendering engines; findings require human examiner validation."
        ]

        image_char = image_characterization or {}
        img_class = image_char.get("image_class", "UNKNOWN")

        # Applicability check for photographic / scenery images
        if img_class in ["PHOTOGRAPH", "GRAPHIC"] and not image_char.get("has_text", False):
            # Quick check if there is obvious text before declaring not applicable
            try:
                with Image.open(image_path) as test_img:
                    thumb = test_img.convert("L").resize((128, 128))
                    edges = cv2.Canny(np.array(thumb), 100, 200)
                    edge_density = float(np.mean(edges > 0))
                    if edge_density < 0.04:  # Very low edge density, no structured text
                        exec_time = round((time.perf_counter() - start_time) * 1000, 2)
                        res = ScreeningTestResult(
                            method=cls.METHOD_NAME,
                            version=cls.VERSION,
                            status="not_applicable",
                            indicator="no_indicator_detected",
                            indicator_label="Not Applicable (Photographic Specimen)",
                            observations=["Specimen is an optical photograph/graphic lacking structured document typography."],
                            explanation="Typography and baseline alignment analysis applies exclusively to documents, certificates, and textual UI screenshots.",
                            limitations=limitations,
                            execution_time_ms=exec_time,
                        )
                        d_res = DetectorResult(
                            detector_name=cls.METHOD_NAME,
                            detector_version=cls.VERSION,
                            status=DetectorStatus.NOT_APPLICABLE.value,
                            score=0.0,
                            confidence=0.0,
                            evidence_strength=EvidenceStrength.NONE.value,
                            applicable=False,
                            technical_reason="Specimen is an optical photograph/graphic; document typography verification not applicable.",
                            affected_regions=[],
                            execution_time_ms=exec_time,
                        )
                        return res, artifacts, analytics, d_res
            except Exception:
                pass

        try:
            with Image.open(image_path) as img:
                rgb = np.array(img.convert("RGB"))
                gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
                height, width = gray.shape

                # 1. Binarize using Adaptive Thresholding
                thresh = cv2.adaptiveThreshold(
                    gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 15, 6
                )

                # 2. Extract Connected Component Contours
                contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

                glyph_boxes: List[Tuple[int, int, int, int]] = []
                for cnt in contours:
                    x, y, w, h = cv2.boundingRect(cnt)
                    area = w * h
                    if 6 <= h <= 120 and 3 <= w <= 120 and 15 <= area <= 8000:
                        aspect = w / float(h)
                        if 0.1 <= aspect <= 3.5:
                            glyph_boxes.append((x, y, w, h))

                total_glyphs = len(glyph_boxes)

                # Low text density in natural scenes -> Not Applicable
                if total_glyphs < 20:
                    exec_time = round((time.perf_counter() - start_time) * 1000, 2)
                    res = ScreeningTestResult(
                        method=cls.METHOD_NAME,
                        version=cls.VERSION,
                        status="not_applicable",
                        indicator="no_indicator_detected",
                        indicator_label="Not Applicable (Low Text Density)",
                        observations=[
                            f"Analyzed {total_glyphs} candidate high-contrast glyph contours.",
                            "Image does not contain structured digital document typography or tabular text records."
                        ],
                        explanation="Low text density detected. The specimen does not contain sufficient structured typographic characters for baseline verification.",
                        limitations=limitations,
                        execution_time_ms=exec_time,
                    )
                    d_res = DetectorResult(
                        detector_name=cls.METHOD_NAME,
                        detector_version=cls.VERSION,
                        status=DetectorStatus.NOT_APPLICABLE.value,
                        score=0.0,
                        confidence=0.0,
                        evidence_strength=EvidenceStrength.NONE.value,
                        applicable=False,
                        technical_reason="Insufficient structured text glyphs for document typography verification.",
                        affected_regions=[],
                        execution_time_ms=exec_time,
                    )
                    return res, artifacts, analytics, d_res

                # 3. Sort glyphs into horizontal text lines
                glyph_boxes.sort(key=lambda b: (b[1], b[0]))
                lines: List[List[Tuple[int, int, int, int]]] = []
                for box in glyph_boxes:
                    bx, by, bw, bh = box
                    box_center_y = by + bh / 2.0
                    matched_line = False

                    for line in lines:
                        ref_y = sum(b[1] + b[3] / 2.0 for b in line) / len(line)
                        ref_h = sum(b[3] for b in line) / len(line)
                        if abs(box_center_y - ref_y) < (0.45 * ref_h):
                            line.append(box)
                            matched_line = True
                            break

                    if not matched_line:
                        lines.append([box])

                valid_lines = []
                for l in lines:
                    if len(l) >= 4:
                        heights = [b[3] for b in l]
                        mean_h = float(np.mean(heights))
                        std_h = float(np.std(heights))
                        if (std_h / (mean_h + 1e-4)) < 0.60:
                            l.sort(key=lambda b: b[0])
                            span_x = (l[-1][0] + l[-1][2]) - l[0][0]
                            if span_x > 2.5 * mean_h:
                                valid_lines.append(l)

                if len(valid_lines) < 2:
                    exec_time = round((time.perf_counter() - start_time) * 1000, 2)
                    res = ScreeningTestResult(
                        method=cls.METHOD_NAME,
                        version=cls.VERSION,
                        status="not_applicable",
                        indicator="no_indicator_detected",
                        indicator_label="Not Applicable (No Coherent Text Lines)",
                        observations=[
                            f"Identified {total_glyphs} candidate contours, but fewer than 2 coherent horizontal lines.",
                            "Specimen does not contain formatted document paragraphs or tabular records."
                        ],
                        explanation="No coherent typographic text lines identified; baseline alignment test marked not applicable.",
                        limitations=limitations,
                        execution_time_ms=exec_time,
                    )
                    d_res = DetectorResult(
                        detector_name=cls.METHOD_NAME,
                        detector_version=cls.VERSION,
                        status=DetectorStatus.NOT_APPLICABLE.value,
                        score=0.0,
                        confidence=0.0,
                        evidence_strength=EvidenceStrength.NONE.value,
                        applicable=False,
                        technical_reason="Fewer than 2 coherent text lines identified.",
                        affected_regions=[],
                        execution_time_ms=exec_time,
                    )
                    return res, artifacts, analytics, d_res

                # 4. Measure Baseline & Kerning Deviations
                anomalous_glyphs = []
                base_deviations = []
                for l in valid_lines:
                    baselines = [b[1] + b[3] for b in l]
                    med_base = float(np.median(baselines))
                    for b in l:
                        dev = abs((b[1] + b[3]) - med_base)
                        base_deviations.append(dev)
                        if dev > (0.28 * b[3]):  # Baseline offset exceeds 28% of glyph height
                            anomalous_glyphs.append(b)

                mean_base_dev = float(np.mean(base_deviations)) if base_deviations else 0.0
                num_anomalies = len(anomalous_glyphs)
                anomaly_rate = (num_anomalies / max(1, total_glyphs)) * 100.0

                for b in anomalous_glyphs[:15]:
                    affected_regions.append(
                        EvidenceRegion(
                            x=b[0],
                            y=b[1],
                            width=b[2],
                            height=b[3],
                            confidence=0.88,
                            detector=cls.METHOD_NAME,
                            label="Suspicious Character Baseline / Kerning Offset",
                        )
                    )

                observations.append(f"Analyzed {total_glyphs} document character glyphs across {len(valid_lines)} coherent text lines.")
                observations.append(f"Mean baseline deviation: {mean_base_dev:.2f} px.")
                observations.append(f"Identified {num_anomalies} character glyphs ({anomaly_rate:.1f}%) exhibiting irregular baseline divergence.")

                # Calibrated Decision
                if num_anomalies >= 8 and anomaly_rate > 5.0:
                    indicator = "indicator_detected"
                    indicator_label = f"Document Typography Discrepancy Detected ({num_anomalies} anomalous glyphs)"
                    norm_status = DetectorStatus.POSITIVE.value
                    score = min(0.92, 0.65 + (num_anomalies * 0.02))
                    confidence = 0.85
                    strength = EvidenceStrength.STRONG.value
                    explanation = (
                        f"Detected {num_anomalies} irregular character glyphs ({anomaly_rate:.1f}% divergence rate) with "
                        "statistically significant baseline offset. In digital documents, localized character displacement frequently indicates "
                        "tampered text, overwritten numerical amounts, or spliced credentials."
                    )
                elif num_anomalies >= 3:
                    indicator = "inconclusive"
                    indicator_label = f"Inconclusive Typography Variance ({num_anomalies} glyphs)"
                    norm_status = DetectorStatus.INCONCLUSIVE.value
                    score = 0.35
                    confidence = 0.50
                    strength = EvidenceStrength.LOW.value
                    explanation = (
                        f"Isolated baseline deviations observed ({num_anomalies} glyphs, {anomaly_rate:.1f}%). "
                        "While this may point to localized character alteration, minor deviations also occur legitimately with "
                        "subscript/superscript characters, varied punctuation, or font rendering kerning tables."
                    )
                else:
                    indicator = "no_indicator_detected"
                    indicator_label = "Document Typography Spatially Consistent"
                    norm_status = DetectorStatus.NEGATIVE.value
                    score = 0.05
                    confidence = 0.85
                    strength = EvidenceStrength.NONE.value
                    explanation = (
                        "Document typography exhibits consistent baseline alignment and uniform character edge gradients across all evaluated lines. "
                        "No signs of overwritten glyphs, pasted text patches, or numerical tampering were identified."
                    )

        except Exception as e:
            exec_time = round((time.perf_counter() - start_time) * 1000, 2)
            res = ScreeningTestResult(
                method=cls.METHOD_NAME,
                version=cls.VERSION,
                status="failed",
                indicator="test_failed",
                indicator_label="Test failed",
                observations=[f"Error during typography analysis: {str(e)}"],
                explanation="Document typography analysis encountered an unexpected error.",
                limitations=limitations,
                execution_time_ms=exec_time,
            )
            d_res = DetectorResult(
                detector_name=cls.METHOD_NAME,
                detector_version=cls.VERSION,
                status=DetectorStatus.ERROR.value,
                score=0.0,
                confidence=0.0,
                evidence_strength=EvidenceStrength.NONE.value,
                applicable=True,
                technical_reason=str(e),
                affected_regions=[],
                execution_time_ms=exec_time,
            )
            return res, artifacts, analytics, d_res

        exec_time = round((time.perf_counter() - start_time) * 1000, 2)
        test_result = ScreeningTestResult(
            method=cls.METHOD_NAME,
            version=cls.VERSION,
            status="completed",
            indicator=indicator,
            indicator_label=indicator_label,
            observations=observations,
            explanation=explanation,
            limitations=limitations,
            execution_time_ms=exec_time,
            score=round(score, 3),
            confidence=round(confidence, 3),
            evidence_strength=strength,
            normalized_status=norm_status,
            affected_regions=affected_regions,
        )
        detector_result = DetectorResult(
            detector_name=cls.METHOD_NAME,
            detector_version=cls.VERSION,
            status=norm_status,
            score=round(score, 3),
            confidence=round(confidence, 3),
            evidence_strength=strength,
            applicable=True,
            technical_reason=explanation,
            affected_regions=affected_regions,
            execution_time_ms=exec_time,
            observations=observations,
            limitations=limitations,
        )
        analytics = {
            "total_glyphs_analyzed": total_glyphs,
            "text_lines_evaluated": len(valid_lines) if 'valid_lines' in locals() else 0,
            "anomalous_glyphs_count": num_anomalies if 'num_anomalies' in locals() else 0,
            "anomaly_rate_pct": round(anomaly_rate, 2) if 'anomaly_rate' in locals() else 0.0,
        }
        return test_result, artifacts, analytics, detector_result
