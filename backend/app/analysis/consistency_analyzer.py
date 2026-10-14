import time
from pathlib import Path
from typing import Dict, Any, List, Tuple
from PIL import Image
import numpy as np
import cv2

from app.core.config import settings
from app.schemas.examination import ScreeningTestResult


class ConsistencyAnalyzer:
    METHOD_NAME = "image_consistency_checks"
    VERSION = "1.0.0"

    @classmethod
    def analyze(
        cls,
        image_path: Path,
        examination_id: str,
        media_type: str,
        metadata_dict: Dict[str, Any],
    ) -> Tuple[ScreeningTestResult, Dict[str, str], Dict[str, Any]]:
        start_time = time.perf_counter()
        observations: List[str] = []
        artifacts: Dict[str, str] = {}
        analytics: Dict[str, Any] = {}
        limitations: List[str] = [
            "Natural lighting variations, focal depth of field (bokeh), and shadows cause organic noise differences.",
            "Cropping or non-standard aspect ratios frequently occur for legitimate design or display purposes.",
            "Statistical consistency tests provide descriptive indicators, not definitive proof of tampering."
        ]

        indicator = "no_indicator_detected"
        indicator_label = "No indicator detected by this test"
        indicator_reasons = []

        try:
            with Image.open(image_path) as img:
                width, height = img.size
                aspect_ratio = width / height if height > 0 else 1.0
                total_pixels = width * height
                color_mode = img.mode

                observations.append(f"Image geometry: {width} x {height} px ({total_pixels / 1_000_000:.2f} Megapixels).")
                observations.append(f"Aspect ratio: {aspect_ratio:.2f}:1.")
                observations.append(f"Color space mode: {color_mode}.")

                # Convert to RGB numpy array
                rgb_img = np.array(img.convert("RGB"))

                # 1. Color channel statistics
                r_channel = rgb_img[:, :, 0]
                g_channel = rgb_img[:, :, 1]
                b_channel = rgb_img[:, :, 2]

                r_mean, r_std = float(np.mean(r_channel)), float(np.std(r_channel))
                g_mean, g_std = float(np.mean(g_channel)), float(np.std(g_channel))
                b_mean, b_std = float(np.mean(b_channel)), float(np.std(b_channel))

                analytics["channels"] = {
                    "red": {"mean": round(r_mean, 1), "std": round(r_std, 1)},
                    "green": {"mean": round(g_mean, 1), "std": round(g_std, 1)},
                    "blue": {"mean": round(b_mean, 1), "std": round(b_std, 1)},
                }
                observations.append(f"Color balance averages: R={r_mean:.1f}, G={g_mean:.1f}, B={b_mean:.1f}.")

                # Check for extreme clipping
                r_clipped = np.sum((r_channel < 2) | (r_channel > 253)) / total_pixels * 100
                g_clipped = np.sum((g_channel < 2) | (g_channel > 253)) / total_pixels * 100
                b_clipped = np.sum((b_channel < 2) | (b_channel > 253)) / total_pixels * 100
                max_clip = max(r_clipped, g_clipped, b_clipped)
                if max_clip > 35.0:
                    observations.append(f"Significant dynamic range clipping observed ({max_clip:.1f}% extreme values).")

                # 2. High-Frequency Noise & Sensor Consistency (Laplacian Filter)
                gray = cv2.cvtColor(rgb_img, cv2.COLOR_RGB2GRAY)
                laplacian = cv2.Laplacian(gray, cv2.CV_64F)
                overall_noise_var = float(laplacian.var())
                observations.append(f"Overall high-frequency variance (sharpness/noise metric): {overall_noise_var:.1f}.")

                # Divide into 4 quadrants to detect severe spatial noise asymmetry
                mid_y, mid_x = height // 2, width // 2
                q1 = laplacian[:mid_y, :mid_x].var()
                q2 = laplacian[:mid_y, mid_x:].var()
                q3 = laplacian[mid_y:, :mid_x].var()
                q4 = laplacian[mid_y:, mid_x:].var()
                quad_vars = [float(q1), float(q2), float(q3), float(q4)]
                max_q = max(quad_vars)
                min_q = min(quad_vars)
                ratio_q = max_q / (min_q + 1e-4)

                analytics["quadrant_variance"] = [round(v, 1) for v in quad_vars]

                # Generate a normalized noise map visualization
                noise_norm = cv2.normalize(np.abs(laplacian), None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)
                noise_filename = f"{examination_id}_noise.png"
                noise_path = settings.ARTIFACTS_DIR / noise_filename
                cv2.imwrite(str(noise_path), noise_norm)
                artifacts["noise_map"] = noise_filename

                # 3. Metadata vs Image Dimensional Consistency
                exif_width = metadata_dict.get("ExifImageWidth") or metadata_dict.get("ImageWidth")
                exif_height = metadata_dict.get("ExifImageLength") or metadata_dict.get("ImageLength")
                if exif_width and exif_height:
                    try:
                        ew, eh = int(str(exif_width).split()[0]), int(str(exif_height).split()[0])
                        if ew != width or eh != height:
                            observations.append(
                                f"Metadata dimension discrepancy: EXIF reports {ew}x{eh}, but pixel grid is {width}x{height}."
                            )
                            indicator_reasons.append("EXIF dimensions mismatch physical pixel dimensions")
                    except Exception:
                        pass

                # Evaluate consistency observations
                if indicator_reasons:
                    indicator = "indicator_detected"
                    indicator_label = "Indicator detected"
                    explanation = (
                        f"Image consistency checks identified anomalies: {', '.join(indicator_reasons)}. "
                        "This indicates the image has been re-cropped, resized, or modified after the initial "
                        "EXIF header was created."
                    )
                elif ratio_q > 12.0 and overall_noise_var > 150.0:
                    indicator = "inconclusive"
                    indicator_label = "Inconclusive"
                    explanation = (
                        f"Significant spatial high-frequency variance was observed between image quadrants "
                        f"(ratio {ratio_q:.1f}:1). While this may indicate composite insertion of elements with "
                        "differing noise characteristics, it is also standard for photographs with shallow depth of "
                        "field (bokeh) or smooth background skies. Human manual inspection is advised."
                    )
                else:
                    indicator = "no_indicator_detected"
                    indicator_label = "No indicator detected by this test"
                    explanation = (
                        "Image geometry, color channel balance, and noise distribution exhibit standard physical "
                        "consistency. No dimension conflicts or unexplained severe structural discrepancies were identified."
                    )

        except Exception as e:
            exec_time = round((time.perf_counter() - start_time) * 1000, 2)
            test_result = ScreeningTestResult(
                method=cls.METHOD_NAME,
                version=cls.VERSION,
                status="failed",
                indicator="test_failed",
                indicator_label="Test failed",
                observations=[f"Error during consistency analysis: {str(e)}"],
                explanation="Image consistency analysis encountered an unexpected exception.",
                limitations=limitations,
                execution_time_ms=exec_time,
            )
            return test_result, artifacts, analytics

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
