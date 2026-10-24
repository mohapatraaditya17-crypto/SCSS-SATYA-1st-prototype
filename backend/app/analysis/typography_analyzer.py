import time
from pathlib import Path
from typing import Dict, Any, List, Tuple
from PIL import Image
import numpy as np
import cv2

from app.core.config import settings
from app.schemas.examination import ScreeningTestResult


class TypographyAnalyzer:
    METHOD_NAME = "document_typography_and_alignment"
    VERSION = "1.0.0"

    @classmethod
    def analyze(
        cls,
        image_path: Path,
        examination_id: str,
        media_type: str,
    ) -> Tuple[ScreeningTestResult, Dict[str, str], Dict[str, Any]]:
        start_time = time.perf_counter()
        observations: List[str] = []
        artifacts: Dict[str, str] = {}
        analytics: Dict[str, Any] = {}
        limitations: List[str] = [
            "Typography and alignment analysis operates on document glyphs, certificates, screenshots, and tabular records; natural photography lacking text is skipped or reports minimal glyph counts.",
            "Handwritten text, stylized cursive fonts, or intentionally staggered graphic typography can produce organic baseline variances.",
            "Sub-pixel anti-aliasing differences vary across operating systems and rendering engines; findings require human examiner validation."
        ]

        try:
            with Image.open(image_path) as img:
                rgb = np.array(img.convert("RGB"))
                gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
                height, width = gray.shape

                # 1. Binarize using Adaptive Thresholding to segment characters
                thresh = cv2.adaptiveThreshold(
                    gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 15, 6
                )

                # 2. Extract Connected Component Contours
                contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

                # Filter contours by typical character glyph dimensions (height 6px to 120px, aspect ratio 0.1 to 3.5)
                glyph_boxes: List[Tuple[int, int, int, int]] = []
                for cnt in contours:
                    x, y, w, h = cv2.boundingRect(cnt)
                    area = w * h
                    if 6 <= h <= 120 and 3 <= w <= 120 and 15 <= area <= 8000:
                        aspect = w / float(h)
                        if 0.1 <= aspect <= 3.5:
                            glyph_boxes.append((x, y, w, h))

                total_glyphs = len(glyph_boxes)

                # If very few glyphs detected (natural scenery, abstract graphic, no text)
                if total_glyphs < 15:
                    exec_time = round((time.perf_counter() - start_time) * 1000, 2)
                    test_result = ScreeningTestResult(
                        method=cls.METHOD_NAME,
                        version=cls.VERSION,
                        status="completed",
                        indicator="no_indicator_detected",
                        indicator_label="No indicator detected by this test",
                        observations=[
                            f"Analyzed {total_glyphs} candidate high-contrast glyph contours.",
                            "Image does not appear to contain structured digital document typography or tabular text records."
                        ],
                        explanation=(
                            "Low text density detected. The specimen does not contain sufficient structured typographic characters "
                            "or tabular records to execute document alignment and kerning verification."
                        ),
                        limitations=limitations,
                        execution_time_ms=exec_time,
                    )
                    return test_result, artifacts, analytics

                # 3. Sort glyphs into horizontal text lines
                # Sort primarily by vertical Y coordinate
                glyph_boxes.sort(key=lambda b: (b[1], b[0]))

                lines: List[List[Tuple[int, int, int, int]]] = []
                for box in glyph_boxes:
                    bx, by, bw, bh = box
                    box_center_y = by + bh / 2.0
                    matched_line = False

                    for line in lines:
                        ref_y = sum(b[1] + b[3] / 2.0 for b in line) / len(line)
                        ref_h = sum(b[3] for b in line) / len(line)
                        # If vertical center is within 40% of line average height
                        if abs(box_center_y - ref_y) < (0.45 * ref_h):
                            line.append(box)
                            matched_line = True
                            break

                    if not matched_line:
                        lines.append([box])

                # Filter lines: real text lines have consistent glyph heights and horizontal span
                valid_lines = []
                for l in lines:
                    if len(l) >= 4:
                        heights = [b[3] for b in l]
                        mean_h = float(np.mean(heights))
                        std_h = float(np.std(heights))
                        # Text lines have reasonably uniform character heights
                        if (std_h / (mean_h + 1e-4)) < 0.60:
                            l.sort(key=lambda b: b[0])
                            # Check horizontal span
                            span_x = (l[-1][0] + l[-1][2]) - l[0][0]
                            if span_x > 2.5 * mean_h:
                                valid_lines.append(l)

                if len(valid_lines) < 2:
                    exec_time = round((time.perf_counter() - start_time) * 1000, 2)
                    test_result = ScreeningTestResult(
                        method=cls.METHOD_NAME,
                        version=cls.VERSION,
                        status="completed",
                        indicator="no_indicator_detected",
                        indicator_label="No Structured Typography Found",
                        observations=[
                            f"Identified {total_glyphs} candidate high-contrast contours.",
                            "No coherent typographic text lines identified; specimen appears to be photographic or natural scenery content."
                        ],
                        explanation=(
                            "Low coherent text density detected. The specimen does not contain structured typographic character lines "
                            "or tabular records to execute document baseline and kerning verification."
                        ),
                        limitations=limitations,
                        execution_time_ms=exec_time,
                    )
                    return test_result, artifacts, {
                        "total_glyphs_analyzed": total_glyphs,
                        "text_lines_evaluated": 0,
                        "anomalous_glyphs_count": 0,
                        "alignment_anomalies_detected": 0,
                        "anomalous_regions": [],
                    }

                # 4. Analyze Baseline Alignment & Kerning Regularity
                sobel_x = cv2.Sobel(gray, cv2.CV_32F, 1, 0, ksize=3)
                sobel_y = cv2.Sobel(gray, cv2.CV_32F, 0, 1, ksize=3)
                grad_mag = np.sqrt(sobel_x ** 2 + sobel_y ** 2)

                anomalous_glyphs: List[Tuple[int, int, int, int]] = []
                regular_glyphs: List[Tuple[int, int, int, int]] = []
                baseline_deviations = []

                for line in valid_lines:
                    baselines = [b[1] + b[3] for b in line]  # bottom Y coordinate of character
                    med_baseline = float(np.median(baselines))
                    avg_h = float(np.mean([b[3] for b in line]))

                    # Estimate standard descender drop (~0.25 - 0.35 of character height)
                    descender_baseline = med_baseline + 0.30 * avg_h

                    # Edge sharpness per glyph
                    glyph_sharpness = []
                    for b in line:
                        bx, by, bw, bh = b
                        roi_grad = grad_mag[by:by + bh, bx:bx + bw]
                        glyph_sharpness.append(float(np.mean(roi_grad)))
                    med_sharpness = float(np.median(glyph_sharpness))

                    for idx, b in enumerate(line):
                        bx, by, bw, bh = b
                        bottom_y = by + bh
                        base_diff_main = abs(bottom_y - med_baseline)
                        base_diff_desc = abs(bottom_y - descender_baseline)
                        base_diff = min(base_diff_main, base_diff_desc)
                        baseline_deviations.append(base_diff)

                        # Check for anomalous baseline displacement (> 38% of character height) or extreme sharpness mismatch
                        is_anomalous = False
                        if base_diff > (0.38 * avg_h) and avg_h > 12:
                            is_anomalous = True

                        if med_sharpness > 15:
                            sharp_ratio = glyph_sharpness[idx] / (med_sharpness + 1e-4)
                            if sharp_ratio > 3.8 or sharp_ratio < 0.20:
                                is_anomalous = True

                        if is_anomalous:
                            anomalous_glyphs.append(b)
                        else:
                            regular_glyphs.append(b)

                # 5. Generate Visual Typography Map
                vis_img = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)

                # Draw regular glyphs in green
                for bx, by, bw, bh in regular_glyphs:
                    cv2.rectangle(vis_img, (bx, by), (bx + bw, by + bh), (0, 200, 0), 1)

                # Draw anomalous glyphs in bold red with highlighted crosshair
                for bx, by, bw, bh in anomalous_glyphs:
                    cv2.rectangle(vis_img, (bx, by), (bx + bw, by + bh), (0, 0, 255), 2)
                    cv2.drawMarker(vis_img, (bx + bw // 2, by + bh), (0, 0, 255), cv2.MARKER_TILTED_CROSS, 8, 2)

                # Draw baseline guide lines for valid lines
                for line in valid_lines:
                    if line:
                        med_y = int(round(np.median([b[1] + b[3] for b in line])))
                        min_x = line[0][0] - 5
                        max_x = line[-1][0] + line[-1][2] + 5
                        cv2.line(vis_img, (max(0, min_x), med_y), (min(width - 1, max_x), med_y), (255, 200, 0), 1, cv2.LINE_4)

                artifact_filename = f"{examination_id}_typography.png"
                artifact_path = settings.ARTIFACTS_DIR / artifact_filename
                cv2.imwrite(str(artifact_path), vis_img)
                artifacts["typography_map"] = artifact_filename

                # Evidentiary metrics
                num_anomalies = len(anomalous_glyphs)
                anomaly_rate = (num_anomalies / float(total_glyphs) * 100.0) if total_glyphs > 0 else 0.0
                mean_base_dev = float(np.mean(baseline_deviations)) if baseline_deviations else 0.0

                analytics["total_glyphs_analyzed"] = total_glyphs
                analytics["text_lines_evaluated"] = len(valid_lines)
                analytics["anomalous_glyphs_count"] = num_anomalies
                analytics["alignment_anomalies_detected"] = num_anomalies
                analytics["anomaly_rate_pct"] = round(float(anomaly_rate), 2)
                analytics["mean_baseline_deviation_px"] = round(float(mean_base_dev), 2)
                analytics["anomalous_regions"] = [
                    {"x": b[0], "y": b[1], "w": b[2], "h": b[3]} for b in anomalous_glyphs[:20]
                ]

                observations.append(f"Analyzed {total_glyphs} document character glyphs across {len(valid_lines)} coherent text lines.")
                observations.append(f"Mean baseline deviation: {mean_base_dev:.2f} px.")
                observations.append(f"Identified {num_anomalies} character glyphs ({anomaly_rate:.1f}%) exhibiting irregular baseline or edge sharpness divergence.")

                if num_anomalies >= 8 and anomaly_rate > 5.0:
                    indicator = "indicator_detected"
                    indicator_label = f"Document Typography Discrepancy Detected ({num_anomalies} anomalous glyphs)"
                    explanation = (
                        f"Detected {num_anomalies} irregular character glyphs ({anomaly_rate:.1f}% divergence rate) with "
                        "statistically significant baseline offset or edge gradient blur discrepancies. "
                        "In digital certificates, invoices, and screenshot records, localized character displacement frequently indicates "
                        "tampered text, overwritten numerical amounts, or spliced credentials."
                    )
                elif num_anomalies >= 3:
                    indicator = "inconclusive"
                    indicator_label = f"Inconclusive Typography Variance ({num_anomalies} glyphs)"
                    explanation = (
                        f"Isolated baseline deviations observed ({num_anomalies} glyphs, {anomaly_rate:.1f}%). "
                        "While this may point to localized character alteration, minor deviations also occur legitimately with "
                        "subscript/superscript characters, varied punctuation, or font rendering kerning tables."
                    )
                else:
                    indicator = "no_indicator_detected"
                    indicator_label = "Document Typography Spatially Consistent"
                    explanation = (
                        "Document typography exhibits consistent baseline alignment and uniform character edge gradients across all evaluated lines. "
                        "No signs of overwritten glyphs, pasted text patches, or numerical tampering were identified."
                    )

        except Exception as e:
            exec_time = round((time.perf_counter() - start_time) * 1000, 2)
            return ScreeningTestResult(
                method=cls.METHOD_NAME,
                version=cls.VERSION,
                status="failed",
                indicator="test_failed",
                indicator_label="Test failed",
                observations=[f"Error during typography analysis: {str(e)}"],
                explanation="Document typography analysis encountered an unexpected error.",
                limitations=limitations,
                execution_time_ms=exec_time,
            ), artifacts, analytics

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
        )
        return test_result, artifacts, analytics
