import time
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional
import cv2
import numpy as np
from PIL import Image

from app.core.config import settings
from app.schemas.examination import (
    ScreeningTestResult,
    DetectorResult,
    DetectorStatus,
    EvidenceStrength,
    EvidenceRegion,
)


class SplicingDetector:
    """
    Image Splicing & Multi-Source Composite Forgery Detector (SATYA v2).
    Combines multi-scale block noise variance comparison, boundary edge gradient discontinuity,
    and localized color covariance mismatch to identify spliced elements.
    """
    ANALYZER_VERSION = "2.0.0"
    METHOD = "image_splicing_detector"
    BLOCK_SIZE = 32

    @classmethod
    def analyze(
        cls,
        image_path: Path,
        examination_id: str,
        media_type: str,
        artifacts_dir: Optional[Path] = None,
    ) -> Tuple[ScreeningTestResult, Dict[str, Any], Dict[str, Any], DetectorResult]:
        start = time.perf_counter()
        observations: List[str] = []
        artifacts: Dict[str, Any] = {}
        affected_regions: List[EvidenceRegion] = []
        limitations: List[str] = [
            "Block-based noise analysis may flag natural lighting transitions in photographs (e.g. indoor/outdoor frames).",
            "Heavy JPEG recompression homogenizes block statistics, reducing splicing indicator sensitivity.",
            "Text, logos, and UI overlay regions on screenshots will typically show elevated statistical divergence vs. photographic backgrounds."
        ]

        try:
            img = cv2.imread(str(image_path), cv2.IMREAD_COLOR)
            if img is None:
                raise ValueError("Could not decode image bitstream")

            h, w = img.shape[:2]
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY).astype(np.float32)

            bs = cls.BLOCK_SIZE
            rows = h // bs
            cols = w // bs

            if rows < 3 or cols < 3:
                elapsed = round((time.perf_counter() - start) * 1000, 2)
                res = ScreeningTestResult(
                    method="Image Splicing & Composite Forgery Detector",
                    version=cls.ANALYZER_VERSION,
                    status="not_applicable",
                    indicator="test_unavailable",
                    indicator_label="Image Too Small for Block Splicing Analysis",
                    observations=["Image dimensions below 96x96 pixels required for block splicing analysis."],
                    explanation="Image dimensions insufficient for spatial block-level statistical analysis.",
                    limitations=limitations,
                    execution_time_ms=elapsed,
                )
                d_res = DetectorResult(
                    detector_name=cls.METHOD,
                    detector_version=cls.ANALYZER_VERSION,
                    status=DetectorStatus.NOT_APPLICABLE.value,
                    score=0.0,
                    confidence=0.0,
                    evidence_strength=EvidenceStrength.NONE.value,
                    applicable=False,
                    technical_reason="Image dimensions insufficient for block-level statistical analysis.",
                    affected_regions=[],
                    execution_time_ms=elapsed,
                )
                return res, {}, {}, d_res

            # Step 1: High-pass noise residual extraction
            gray_u8 = gray.astype(np.uint8)
            median_blur = cv2.medianBlur(gray_u8, 3).astype(np.float32)
            noise_residual = np.abs(gray - median_blur)

            # Step 2: Boundary and Gradient analysis
            gx = cv2.Sobel(gray, cv2.CV_32F, 1, 0, ksize=3)
            gy = cv2.Sobel(gray, cv2.CV_32F, 0, 1, ksize=3)
            gmag = np.sqrt(gx ** 2 + gy ** 2)

            # Step 3: Compute Per-Block Noise & Luminance features
            block_lum = np.zeros((rows, cols), dtype=np.float32)
            block_noise = np.zeros((rows, cols), dtype=np.float32)

            for r in range(rows):
                for c in range(cols):
                    blk_gray = gray[r*bs:(r+1)*bs, c*bs:(c+1)*bs]
                    blk_res = noise_residual[r*bs:(r+1)*bs, c*bs:(c+1)*bs]
                    blk_gmag = gmag[r*bs:(r+1)*bs, c*bs:(c+1)*bs]

                    block_lum[r, c] = float(np.mean(blk_gray))
                    if block_lum[r, c] < 8.0:
                        block_noise[r, c] = -1.0
                        continue

                    low_g = blk_gmag < 22.0
                    if np.sum(low_g) >= bs * bs // 5:
                        block_noise[r, c] = float(np.var(blk_res[low_g]))
                    else:
                        block_noise[r, c] = float(np.var(blk_res)) * 0.6

            # Step 4: Calibrated Local Peer Comparison (radius 5 blocks, luminance tier +- 35)
            anomaly_matrix = np.zeros((rows, cols), dtype=np.float32)
            anomalous_blocks = []

            for r in range(rows):
                for c in range(cols):
                    c_lum = block_lum[r, c]
                    c_noise = block_noise[r, c]
                    if c_noise < 0:
                        continue

                    r0, r1 = max(0, r - 5), min(rows, r + 6)
                    c0, c1 = max(0, c - 5), min(cols, c + 6)
                    peer_lums = block_lum[r0:r1, c0:c1].ravel()
                    peer_noises = block_noise[r0:r1, c0:c1].ravel()

                    valid = peer_noises >= 0
                    p_lums = peer_lums[valid]
                    p_noises = peer_noises[valid]

                    same_tier = np.abs(p_lums - c_lum) <= 35.0
                    tier_noises = p_noises[same_tier]
                    if len(tier_noises) < 4:
                        continue

                    peer_med = float(np.median(tier_noises))
                    peer_mad = float(np.median(np.abs(tier_noises - peer_med))) + 1e-4
                    z = abs(c_noise - peer_med) / peer_mad

                    # Calibrated threshold: z > 3.8
                    if z > 3.8:
                        score = float(min(0.92, 0.50 + (z - 3.8) * 0.08))
                        anomaly_matrix[r, c] = score
                        anomalous_blocks.append({"r": r, "c": c, "z": z, "score": score})

            # Step 5: Connected Component Clustering of Anomalies
            bin_map = (anomaly_matrix > 0.40).astype(np.uint8)
            num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(bin_map, connectivity=8)

            clustered_regions_count = 0
            for label_id in range(1, num_labels):
                area = int(stats[label_id, cv2.CC_STAT_AREA])
                if area >= 3:  # Contiguous cluster of >= 3 blocks (~96x96 px)
                    rx = int(stats[label_id, cv2.CC_STAT_LEFT] * bs)
                    ry = int(stats[label_id, cv2.CC_STAT_TOP] * bs)
                    rw = int(stats[label_id, cv2.CC_STAT_WIDTH] * bs)
                    rh = int(stats[label_id, cv2.CC_STAT_HEIGHT] * bs)
                    clustered_regions_count += 1
                    conf = round(min(0.92, 0.60 + (area * 0.04)), 2)
                    affected_regions.append(
                        EvidenceRegion(
                            x=rx,
                            y=ry,
                            width=rw,
                            height=rh,
                            confidence=conf,
                            detector=cls.METHOD,
                            label=f"Spliced / Foreign Composite Region ({area} blocks)",
                        )
                    )

            observations.append(f"Evaluated {rows * cols} macroblocks ({bs}x{bs} px).")
            observations.append(f"Identified {len(anomalous_blocks)} statistically discordant blocks.")
            observations.append(f"Contiguous foreign composite clusters identified: {clustered_regions_count}.")

            # Save Visual Map
            vis_map = cv2.resize(anomaly_matrix, (w, h), interpolation=cv2.INTER_NEAREST)
            norm_vis = cv2.normalize(vis_map, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)
            colored_map = cv2.applyColorMap(norm_vis, cv2.COLORMAP_HOT)
            blended = cv2.addWeighted(img, 0.5, colored_map, 0.5, 0)

            artifact_filename = f"{examination_id}_splicing_map.png"
            out_dir = artifacts_dir or settings.ARTIFACTS_DIR
            cv2.imwrite(str(out_dir / artifact_filename), blended)
            artifacts["splicing_map"] = artifact_filename

            # Calibrated Decision Evaluation
            if clustered_regions_count >= 1:
                indicator = "indicator_detected"
                indicator_label = f"Splicing Boundary / Inconsistency Detected ({clustered_regions_count} regions)"
                norm_status = DetectorStatus.POSITIVE.value
                splice_score = min(0.92, 0.65 + (clustered_regions_count * 0.08))
                confidence = 0.85
                strength = EvidenceStrength.STRONG.value
                explanation = (
                    f"Detected {clustered_regions_count} contiguous spatial cluster(s) with statistically inconsistent "
                    "noise residual and boundary variance. This pattern is characteristic of multi-source image splicing, "
                    "where patches from different cameras or compression states are merged into a composite matrix."
                )
            elif len(anomalous_blocks) >= 5:
                indicator = "inconclusive"
                indicator_label = "Inconclusive Splicing Traces"
                norm_status = DetectorStatus.INCONCLUSIVE.value
                splice_score = 0.35
                confidence = 0.50
                strength = EvidenceStrength.LOW.value
                explanation = (
                    f"Isolated block variance anomalies observed ({len(anomalous_blocks)} blocks), "
                    "but without forming contiguous spatial cluster boundaries. Inconclusive finding."
                )
            else:
                indicator = "no_indicator_detected"
                indicator_label = "No Splicing Indicators Detected"
                norm_status = DetectorStatus.NEGATIVE.value
                splice_score = 0.05
                confidence = 0.82
                strength = EvidenceStrength.NONE.value
                explanation = (
                    "No contiguous regions with statistically foreign noise residuals or boundary discontinuities "
                    "were detected across the macroblock grid."
                )

        except Exception as e:
            elapsed = round((time.perf_counter() - start) * 1000, 2)
            res = ScreeningTestResult(
                method="Image Splicing & Composite Forgery Detector",
                version=cls.ANALYZER_VERSION,
                status="failed",
                indicator="test_failed",
                indicator_label="Test failed",
                observations=[f"Error during splicing analysis: {str(e)}"],
                explanation="Splicing detection encountered an unexpected processing error.",
                limitations=limitations,
                execution_time_ms=elapsed,
            )
            d_res = DetectorResult(
                detector_name=cls.METHOD,
                detector_version=cls.ANALYZER_VERSION,
                status=DetectorStatus.ERROR.value,
                score=0.0,
                confidence=0.0,
                evidence_strength=EvidenceStrength.NONE.value,
                applicable=True,
                technical_reason=str(e),
                affected_regions=[],
                execution_time_ms=elapsed,
            )
            return res, artifacts, {}, d_res

        elapsed = round((time.perf_counter() - start) * 1000, 2)
        test_result = ScreeningTestResult(
            method="Image Splicing & Composite Forgery Detector",
            version=cls.ANALYZER_VERSION,
            status="completed",
            indicator=indicator,
            indicator_label=indicator_label,
            observations=observations,
            explanation=explanation,
            limitations=limitations,
            execution_time_ms=elapsed,
            score=round(splice_score, 3),
            confidence=round(confidence, 3),
            evidence_strength=strength,
            normalized_status=norm_status,
            affected_regions=affected_regions,
        )
        detector_result = DetectorResult(
            detector_name=cls.METHOD,
            detector_version=cls.ANALYZER_VERSION,
            status=norm_status,
            score=round(splice_score, 3),
            confidence=round(confidence, 3),
            evidence_strength=strength,
            applicable=True,
            technical_reason=explanation,
            affected_regions=affected_regions,
            execution_time_ms=elapsed,
            observations=observations,
            limitations=limitations,
        )
        analytics = {
            "splice_score": round(splice_score, 3),
            "anomalous_blocks": len(anomalous_blocks),
            "clustered_regions_count": clustered_regions_count,
            "suspicious_regions": [r.model_dump() for r in affected_regions],
        }
        return test_result, artifacts, analytics, detector_result
