import io
import time
from pathlib import Path
from typing import Dict, Any, List, Tuple
from PIL import Image, ImageChops, ImageEnhance
import numpy as np

from app.core.config import settings
from app.schemas.examination import ScreeningTestResult


class ELAAnalyzer:
    METHOD_NAME = "error_level_analysis"
    VERSION = "1.0.0"
    JPEG_RECOMPRESSION_QUALITY = 90
    SCALE_FACTOR = 15

    @classmethod
    def analyze(
        cls,
        image_path: Path,
        examination_id: str,
        media_type: str,
    ) -> Tuple[ScreeningTestResult, Dict[str, str]]:
        start_time = time.perf_counter()
        observations: List[str] = []
        artifacts: Dict[str, str] = {}
        limitations: List[str] = [
            "Error Level Analysis is an exploratory visualization and does NOT provide definitive proof of tampering.",
            "High-contrast edges, complex textures, text overlays, and dark-to-light transitions naturally exhibit elevated error levels.",
            "Multiple re-saves of an authentic image will flatten ELA variance, potentially masking spliced regions.",
            "ELA is scientifically valid only for lossy discrete cosine transform (DCT) JPEG images."
        ]

        # 1. Format applicability check
        if media_type != "image/jpeg":
            exec_time = round((time.perf_counter() - start_time) * 1000, 2)
            test_result = ScreeningTestResult(
                method=cls.METHOD_NAME,
                version=cls.VERSION,
                status="not_applicable",
                indicator="test_unavailable",
                indicator_label="Test unavailable",
                observations=[
                    f"Image media type is '{media_type}'.",
                    "Error Level Analysis operates on lossy JPEG DCT quantization grids and is not applicable to lossless formats (PNG/WebP).",
                    "No synthetic recompression executed to prevent generating misleading artifacts."
                ],
                explanation=(
                    f"Error Level Analysis (ELA) is not applicable for {media_type} images. "
                    "ELA analyzes compression rate discrepancies across JPEG 8x8 DCT macroblocks. "
                    "Running ELA on lossless formats like PNG produces artificial noise unrelated to real compression history."
                ),
                limitations=limitations,
                execution_time_ms=exec_time,
            )
            return test_result, artifacts

        # 2. Perform ELA on JPEG
        try:
            with Image.open(image_path) as original:
                rgb_original = original.convert("RGB")

                # Resave in-memory at controlled standard quality
                buffer = io.BytesIO()
                rgb_original.save(buffer, "JPEG", quality=cls.JPEG_RECOMPRESSION_QUALITY)
                buffer.seek(0)
                recompressed = Image.open(buffer)

                # Compute absolute channel difference
                diff = ImageChops.difference(rgb_original, recompressed)

                # Compute quantitative statistics via numpy
                diff_arr = np.array(diff, dtype=np.float32)
                mean_error = float(np.mean(diff_arr))
                max_error = float(np.max(diff_arr))
                std_error = float(np.std(diff_arr))

                # Threshold of high error pixels (> 25)
                high_error_ratio = float(np.sum(diff_arr > 25.0) / diff_arr.size) * 100.0

                # Amplify difference for visual examination
                # Find maximum extrema to auto-scale if possible, or use standard fixed scale
                extrema = diff.getextrema()
                max_diff = max([ex[1] for ex in extrema])
                scale = 255.0 / max_diff if max_diff > 0 else 1.0
                scale = min(scale, float(cls.SCALE_FACTOR))

                enhanced = ImageEnhance.Brightness(diff).enhance(scale)

                # Save derived ELA artifact
                artifact_filename = f"{examination_id}_ela.png"
                artifact_path = settings.ARTIFACTS_DIR / artifact_filename
                enhanced.save(artifact_path, "PNG")
                artifacts["ela_heatmap"] = artifact_filename

            observations.append(f"Recompression standard baseline: JPEG Q={cls.JPEG_RECOMPRESSION_QUALITY}.")
            observations.append(f"Residual metrics: Mean={mean_error:.2f}, StdDev={std_error:.2f}, Max={max_error:.0f}.")
            observations.append(f"High-error pixel ratio: {high_error_ratio:.2f}%.")
            observations.append(f"Visual heatmap generated with {scale:.1f}x amplification factor.")

            # Formulate indicator cautious summary
            if std_error > 8.0 and high_error_ratio > 5.0:
                indicator = "indicator_detected"
                indicator_label = "Indicator detected"
                explanation = (
                    f"Error Level Analysis identified noticeable spatial variance in compression error levels "
                    f"(StdDev={std_error:.2f}, high-error pixels={high_error_ratio:.2f}%). "
                    "Certain regions degraded at significantly different rates than the background during standard recompression. "
                    "This pattern frequently occurs when content from a source with different compression history is spliced into an image. "
                    "However, sharp textural boundaries or high-frequency detail can also create elevated ELA responses; "
                    "expert manual verification is required."
                )
            elif mean_error < 0.8 and std_error < 1.5:
                indicator = "inconclusive"
                indicator_label = "Inconclusive"
                explanation = (
                    "Error level residuals across the image are exceptionally low and uniform. "
                    "This typically indicates the image has been re-saved multiple times at high quality or flattened, "
                    "which homogenizes error levels across all regions. An inconclusive finding is recorded."
                )
            else:
                indicator = "no_indicator_detected"
                indicator_label = "No indicator detected by this test"
                explanation = (
                    f"Compression error levels are generally uniform across the macroblock grid "
                    f"(Mean={mean_error:.2f}, StdDev={std_error:.2f}). No glaring localized error discrepancies "
                    "were detected under standard recompression. This suggests a consistent compression history, "
                    "though sophisticated blending cannot be entirely ruled out."
                )

        except Exception as e:
            exec_time = round((time.perf_counter() - start_time) * 1000, 2)
            test_result = ScreeningTestResult(
                method=cls.METHOD_NAME,
                version=cls.VERSION,
                status="failed",
                indicator="test_failed",
                indicator_label="Test failed",
                observations=[f"Error during ELA execution: {str(e)}"],
                explanation="Error Level Analysis failed to complete due to an internal decoding exception.",
                limitations=limitations,
                execution_time_ms=exec_time,
            )
            return test_result, artifacts

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
        return test_result, artifacts
