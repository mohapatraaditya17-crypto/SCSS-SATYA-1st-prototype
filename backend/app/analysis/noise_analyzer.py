import time
from pathlib import Path
from typing import Dict, Any, List, Tuple
from PIL import Image
import numpy as np
import cv2

from app.core.config import settings
from app.schemas.examination import ScreeningTestResult


class NoiseAnalyzer:
    METHOD_NAME = "noise_residual_analysis"
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
            "Noise residual analysis evaluates sensor and raster noise variance; natural shadows and bokeh can introduce organic variance.",
            "Heavy lossy compression or median filtering can flatten high-frequency noise, potentially masking spliced regions.",
            "Solid graphic areas or digital interface elements (text, dark bars) exhibit zero sensor noise naturally."
        ]

        try:
            with Image.open(image_path) as img:
                rgb = np.array(img.convert("RGB"))
                gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
                height, width = gray.shape

                # 1. Compute 2D High-Pass Median Filter Noise Residual
                # Residual = |Original - MedianFiltered|
                median_filtered = cv2.medianBlur(gray, 3)
                residual = cv2.absdiff(gray, median_filtered).astype(np.float32)

                mean_noise = float(np.mean(residual))
                std_noise = float(np.std(residual))
                max_noise = float(np.max(residual))

                # Compute Signal-to-Noise Ratio (SNR) in dB
                signal_level = float(np.mean(gray))
                snr_db = 20.0 * np.log10(signal_level / (std_noise + 1e-4)) if signal_level > 0 and std_noise > 0 else 0.0

                # 2. Edge-Suppressed Block-based local noise variance analysis (16x16 macroblocks)
                gray_f32 = gray.astype(np.float32)
                gx = cv2.Sobel(gray_f32, cv2.CV_32F, 1, 0, ksize=3)
                gy = cv2.Sobel(gray_f32, cv2.CV_32F, 0, 1, ksize=3)
                gmag = np.sqrt(gx ** 2 + gy ** 2)

                block_size = 16
                h_blocks = max(1, height // block_size)
                w_blocks = max(1, width // block_size)
                variance_map = np.zeros((h_blocks, w_blocks), dtype=np.float32)

                valid_vars = []
                for y in range(h_blocks):
                    for x in range(w_blocks):
                        blk_res = residual[y * block_size:(y + 1) * block_size, x * block_size:(x + 1) * block_size]
                        blk_gmag = gmag[y * block_size:(y + 1) * block_size, x * block_size:(x + 1) * block_size]
                        blk_gray = gray[y * block_size:(y + 1) * block_size, x * block_size:(x + 1) * block_size]
                        blk_mean = float(np.mean(blk_gray))

                        # Mask low-gradient pixels in block to measure pure noise without edge contamination
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

                # Statistical Kurtosis of noise residual (measures heavy-tailed anomalous peaks)
                if std_noise > 1e-4:
                    normalized_residual = (residual - mean_noise) / std_noise
                    kurtosis = float(np.mean(normalized_residual ** 4) - 3.0)
                else:
                    kurtosis = 0.0

                analytics["mean_noise"] = round(float(mean_noise), 3)
                analytics["std_noise"] = round(float(std_noise), 3)
                analytics["snr_db"] = round(float(snr_db), 2)
                analytics["kurtosis"] = round(float(kurtosis), 2)
                analytics["inhomogeneity_ratio"] = round(float(inhomogeneity_ratio), 2)

                # 3. Generate Visual Heatmap Artifact
                # Resize variance map to original image dimensions for heatmap display
                resized_var_map = cv2.resize(variance_map, (width, height), interpolation=cv2.INTER_NEAREST)
                norm_var = cv2.normalize(resized_var_map, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)
                colored_heatmap = cv2.applyColorMap(norm_var, cv2.COLORMAP_INFERNO)

                # Overlay slightly on original grayscale for spatial orientation
                gray_bgr = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
                blended = cv2.addWeighted(gray_bgr, 0.4, colored_heatmap, 0.6, 0)

                artifact_filename = f"{examination_id}_noise_residual.png"
                artifact_path = settings.ARTIFACTS_DIR / artifact_filename
                cv2.imwrite(str(artifact_path), blended)
                artifacts["noise_residual_map"] = artifact_filename

                # 4. Formulate Evidentiary Observations
                observations.append(f"High-pass median noise residual: Mean={mean_noise:.2f}, StdDev={std_noise:.2f}, Max={max_noise:.0f}.")
                observations.append(f"Estimated Signal-to-Noise Ratio (SNR): {snr_db:.1f} dB.")
                observations.append(f"Noise distribution Kurtosis: {kurtosis:.2f} (anomalous tail metric).")
                observations.append(f"Robust block variance inhomogeneity ratio (P95/P10): {inhomogeneity_ratio:.1f}:1 across {h_blocks * w_blocks} blocks.")

                # Assess findings
                if inhomogeneity_ratio > 22.0 and kurtosis > 18.0:
                    indicator = "indicator_detected"
                    indicator_label = f"Local Noise Inhomogeneity Detected (Ratio {inhomogeneity_ratio:.1f}:1)"
                    explanation = (
                        f"Abnormal local noise inhomogeneity detected (variance ratio {inhomogeneity_ratio:.1f}:1, kurtosis {kurtosis:.2f}). "
                        "Certain image regions contain noise distributions inconsistent with the rest of the image matrix, "
                        "frequently caused by foreign patch splicing, compositing, or local blurring."
                    )
                elif inhomogeneity_ratio > 12.0:
                    indicator = "inconclusive"
                    indicator_label = f"Moderate Noise Variance Variance ({inhomogeneity_ratio:.1f}:1)"
                    explanation = (
                        f"Moderate noise variance divergence observed (ratio {inhomogeneity_ratio:.1f}:1). "
                        "While this can indicate localized editing, it also naturally occurs in images with mixed text/solid graphic "
                        "elements, screenshots with flat backgrounds, or optical depth of field."
                    )
                else:
                    indicator = "no_indicator_detected"
                    indicator_label = "Noise Residual Distribution Spatially Consistent"
                    explanation = (
                        "Noise residual variance exhibits consistent spatial distribution across the image grid. "
                        "No statistically significant foreign noise patches or spliced boundaries were identified."
                    )

        except Exception as e:
            exec_time = round((time.perf_counter() - start_time) * 1000, 2)
            return ScreeningTestResult(
                method=cls.METHOD_NAME,
                version=cls.VERSION,
                status="failed",
                indicator="test_failed",
                indicator_label="Test failed",
                observations=[f"Error during noise analysis: {str(e)}"],
                explanation="Noise residual screening encountered an unexpected error.",
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
