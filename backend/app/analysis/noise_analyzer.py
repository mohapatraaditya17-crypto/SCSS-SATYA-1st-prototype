import time
from pathlib import Path
from typing import Dict, Any, List, Tuple
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


class NoiseAnalyzer:
    """
    Multi-Scale Noise Residual & Inconsistency Forensic Analyzer (SATYA v2).
    Calibrated to separate natural photographic texture variance (e.g. textured foliage vs flat sky)
    from localized foreign noise patches caused by splicing, compositing, or retouching.
    """
    METHOD_NAME = "noise_residual_analysis"
    VERSION = "2.0.0"

    @classmethod
    def analyze(
        cls,
        image_path: Path,
        examination_id: str,
        media_type: str,
    ) -> Tuple[ScreeningTestResult, Dict[str, str], Dict[str, Any], DetectorResult]:
        start_time = time.perf_counter()
        observations: List[str] = []
        artifacts: Dict[str, str] = {}
        analytics: Dict[str, Any] = {}
        affected_regions: List[EvidenceRegion] = []
        limitations: List[str] = [
            "Noise residual analysis evaluates sensor and raster noise variance; natural shadows and bokeh can introduce organic variance.",
            "Heavy lossy compression or median filtering can flatten high-frequency noise, potentially masking spliced regions.",
            "Solid graphic areas or digital interface elements (text, dark bars) exhibit zero sensor noise naturally."
        ]

        try:
            with Image.open(image_path) as img:
                rgb = np.array(img.convert("RGB"))
                gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
                height, width = gray.shape

                # 1. 2D High-Pass Median Filter Noise Residual
                median_filtered = cv2.medianBlur(gray, 3)
                residual = cv2.absdiff(gray, median_filtered).astype(np.float32)

                mean_noise = float(np.mean(residual))
                std_noise = float(np.std(residual))
                max_noise = float(np.max(residual))

                signal_level = float(np.mean(gray))
                snr_db = 20.0 * np.log10(signal_level / (std_noise + 1e-4)) if signal_level > 0 and std_noise > 0 else 0.0

                # 2. Block-based local noise variance analysis (16x16 macroblocks)
                gray_f32 = gray.astype(np.float32)
                gx = cv2.Sobel(gray_f32, cv2.CV_32F, 1, 0, ksize=3)
                gy = cv2.Sobel(gray_f32, cv2.CV_32F, 0, 1, ksize=3)
                gmag = np.sqrt(gx ** 2 + gy ** 2)

                block_size = 16
                h_blocks = max(1, height // block_size)
                w_blocks = max(1, width // block_size)
                variance_map = np.zeros((h_blocks, w_blocks), dtype=np.float32)
                mean_lum_map = np.zeros((h_blocks, w_blocks), dtype=np.float32)

                valid_vars = []
                for y in range(h_blocks):
                    for x in range(w_blocks):
                        blk_res = residual[y * block_size:(y + 1) * block_size, x * block_size:(x + 1) * block_size]
                        blk_gmag = gmag[y * block_size:(y + 1) * block_size, x * block_size:(x + 1) * block_size]
                        blk_gray = gray[y * block_size:(y + 1) * block_size, x * block_size:(x + 1) * block_size]
                        blk_mean = float(np.mean(blk_gray))
                        mean_lum_map[y, x] = blk_mean

                        low_g = blk_gmag < 15.0
                        if np.sum(low_g) > (block_size * block_size * 0.25):
                            b_var = float(np.var(blk_res[low_g]))
                        else:
                            b_var = float(np.var(blk_res))

                        variance_map[y, x] = b_var
                        if 12 <= blk_mean <= 243:
                            valid_vars.append(b_var)

                if len(valid_vars) > 10:
                    p95 = float(np.percentile(valid_vars, 95))
                    p10 = float(np.percentile(valid_vars, 10))
                    inhomogeneity_ratio = p95 / max(p10, 0.4)
                else:
                    inhomogeneity_ratio = float(np.max(variance_map)) / max(float(np.min(variance_map)), 1.0)

                # Statistical Kurtosis
                if std_noise > 1e-4:
                    normalized_residual = (residual - mean_noise) / std_noise
                    kurtosis = float(np.mean(normalized_residual ** 4) - 3.0)
                else:
                    kurtosis = 0.0

                # 3. SATYA v2 Localized Outlier Cluster Detection:
                # Compare each block to surrounding peers with similar luminance (+- 30 DN)
                anomalous_blocks = []
                for by in range(h_blocks):
                    for bx in range(w_blocks):
                        curr_var = variance_map[by, bx]
                        curr_lum = mean_lum_map[by, bx]
                        # Find peer blocks within radius 4
                        r_y0, r_y1 = max(0, by - 4), min(h_blocks, by + 5)
                        r_x0, r_x1 = max(0, bx - 4), min(w_blocks, bx + 5)
                        peer_lums = mean_lum_map[r_y0:r_y1, r_x0:r_x1].ravel()
                        peer_vars = variance_map[r_y0:r_y1, r_x0:r_x1].ravel()

                        same_tier = np.abs(peer_lums - curr_lum) <= 30.0
                        tier_vars = peer_vars[same_tier]
                        if len(tier_vars) >= 5:
                            med_v = float(np.median(tier_vars))
                            mad_v = float(np.median(np.abs(tier_vars - med_v))) + 1e-4
                            z_v = abs(curr_var - med_v) / mad_v
                            if z_v > 4.5:
                                anomalous_blocks.append((bx, by, z_v))

                # Check if anomalous blocks form contiguous spatial clusters
                cluster_count = 0
                if anomalous_blocks:
                    bin_grid = np.zeros((h_blocks, w_blocks), dtype=np.uint8)
                    for bx, by, _ in anomalous_blocks:
                        bin_grid[by, bx] = 1
                    num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(bin_grid, connectivity=8)
                    for lid in range(1, num_labels):
                        area = stats[lid, cv2.CC_STAT_AREA]
                        if area >= 4:  # At least 4 contiguous anomalous blocks (~64x64 px)
                            cluster_count += 1
                            rx = stats[lid, cv2.CC_STAT_LEFT] * block_size
                            ry = stats[lid, cv2.CC_STAT_TOP] * block_size
                            rw = stats[lid, cv2.CC_STAT_WIDTH] * block_size
                            rh = stats[lid, cv2.CC_STAT_HEIGHT] * block_size
                            affected_regions.append(
                                EvidenceRegion(
                                    x=rx,
                                    y=ry,
                                    width=rw,
                                    height=rh,
                                    confidence=round(min(0.88, 0.60 + (area * 0.04)), 2),
                                    detector=cls.METHOD_NAME,
                                    label=f"Localized Noise Variance Anomaly ({area} blocks)",
                                )
                            )

                analytics["mean_noise"] = round(float(mean_noise), 3)
                analytics["std_noise"] = round(float(std_noise), 3)
                analytics["snr_db"] = round(float(snr_db), 2)
                analytics["kurtosis"] = round(float(kurtosis), 2)
                analytics["inhomogeneity_ratio"] = round(float(inhomogeneity_ratio), 2)
                analytics["anomalous_noise_clusters"] = cluster_count

                # Visual Heatmap
                resized_var_map = cv2.resize(variance_map, (width, height), interpolation=cv2.INTER_NEAREST)
                norm_var = cv2.normalize(resized_var_map, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)
                colored_heatmap = cv2.applyColorMap(norm_var, cv2.COLORMAP_INFERNO)
                gray_bgr = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
                blended = cv2.addWeighted(gray_bgr, 0.4, colored_heatmap, 0.6, 0)

                artifact_filename = f"{examination_id}_noise_residual.png"
                artifact_path = settings.ARTIFACTS_DIR / artifact_filename
                cv2.imwrite(str(artifact_path), blended)
                artifacts["noise_residual_map"] = artifact_filename

                observations.append(f"High-pass median noise residual: Mean={mean_noise:.2f}, StdDev={std_noise:.2f}, Max={max_noise:.0f}.")
                observations.append(f"Estimated Signal-to-Noise Ratio (SNR): {snr_db:.1f} dB.")
                observations.append(f"Noise distribution Kurtosis: {kurtosis:.2f}.")
                observations.append(f"Robust block variance inhomogeneity ratio (P95/P10): {inhomogeneity_ratio:.1f}:1.")
                observations.append(f"Localized noise anomaly clusters confirmed: {cluster_count}.")

                # Calibrated SATYA v2 Decision Logic:
                # Requires a localized spatial cluster to flag positive tampering indicator!
                if cluster_count >= 1 and inhomogeneity_ratio > 35.0:
                    indicator = "indicator_detected"
                    indicator_label = f"Localized Noise Anomaly Cluster Detected ({cluster_count} clusters)"
                    norm_status = DetectorStatus.POSITIVE.value
                    score = min(0.85, 0.55 + (cluster_count * 0.10))
                    confidence = 0.75
                    strength = EvidenceStrength.MODERATE.value
                    explanation = (
                        f"Detected {cluster_count} localized cluster(s) with statistically inconsistent noise variance "
                        f"(P95/P10 ratio {inhomogeneity_ratio:.1f}:1). Specific spatial regions exhibit noise distributions "
                        "sharply diverging from surrounding peers, consistent with foreign patch insertion, splicing, or localized retouching."
                    )
                elif inhomogeneity_ratio > 30.0 or kurtosis > 25.0:
                    indicator = "inconclusive"
                    indicator_label = f"Elevated Scene Inhomogeneity ({inhomogeneity_ratio:.1f}:1)"
                    norm_status = DetectorStatus.INCONCLUSIVE.value
                    score = 0.35
                    confidence = 0.50
                    strength = EvidenceStrength.LOW.value
                    explanation = (
                        f"Elevated scene inhomogeneity observed (ratio {inhomogeneity_ratio:.1f}:1, kurtosis {kurtosis:.2f}), "
                        "but without localized contiguous cluster convergence. This naturally occurs in photographs with mixed "
                        "smooth sky/walls and highly textured foregrounds, or optical depth of field."
                    )
                else:
                    indicator = "no_indicator_detected"
                    indicator_label = "Noise Residual Distribution Spatially Consistent"
                    norm_status = DetectorStatus.NEGATIVE.value
                    score = 0.05
                    confidence = 0.82
                    strength = EvidenceStrength.NONE.value
                    explanation = (
                        "Noise residual variance exhibits consistent spatial distribution across the image grid. "
                        "No statistically significant foreign noise patches or spliced boundaries were identified."
                    )

        except Exception as e:
            exec_time = round((time.perf_counter() - start_time) * 1000, 2)
            res = ScreeningTestResult(
                method=cls.METHOD_NAME,
                version=cls.VERSION,
                status="failed",
                indicator="test_failed",
                indicator_label="Test failed",
                observations=[f"Error during noise analysis: {str(e)}"],
                explanation="Noise residual screening encountered an unexpected error.",
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
        return test_result, artifacts, analytics, detector_result
