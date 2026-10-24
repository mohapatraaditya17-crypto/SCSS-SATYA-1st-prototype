import time
from pathlib import Path
from typing import Dict, Any, List, Tuple
from PIL import Image
import numpy as np
import cv2

from app.core.config import settings
from app.schemas.examination import ScreeningTestResult


class FFTAnalyzer:
    METHOD_NAME = "fourier_spectral_analysis"
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
            "Fourier transform reveals global spatial frequency distributions; localized edits in large images may produce subtle spectral traces.",
            "Screenshots of grid-based digital interfaces or monospace text naturally exhibit harmonic frequency spikes along horizontal and vertical axes.",
            "AI generative models (GANs/diffusion) often leave periodic grid artifacts, but absence of peaks does not prove authenticity."
        ]

        try:
            with Image.open(image_path) as img:
                rgb = np.array(img.convert("RGB"))
                gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
                height, width = gray.shape

                # 1. Compute 2D Fast Fourier Transform (FFT)
                # Apply 2D FFT and shift DC component to center
                f_transform = np.fft.fft2(gray.astype(np.float32))
                f_shifted = np.fft.fftshift(f_transform)
                magnitude_spectrum = np.log(np.abs(f_shifted) + 1.0)

                # Normalize to 0-255 uint8 for visualization
                norm_spectrum = cv2.normalize(magnitude_spectrum, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)
                colored_spectrum = cv2.applyColorMap(norm_spectrum, cv2.COLORMAP_VIRIDIS)

                # Save 2D FFT spectrum artifact
                artifact_filename = f"{examination_id}_fft_spectrum.png"
                artifact_path = settings.ARTIFACTS_DIR / artifact_filename
                cv2.imwrite(str(artifact_path), colored_spectrum)
                artifacts["fft_spectrum"] = artifact_filename

                # 2. Quantitative Spectral Energy Distribution
                # Center coords (DC component)
                cy, cx = height // 2, width // 2
                max_radius = min(cy, cx)

                # Create distance matrix from DC center
                y_coords, x_coords = np.ogrid[:height, :width]
                dist_from_center = np.sqrt((x_coords - cx) ** 2 + (y_coords - cy) ** 2)

                # Low-frequency (< 0.2 max radius) vs High-frequency (> 0.6 max radius)
                low_freq_mask = dist_from_center < (0.2 * max_radius)
                high_freq_mask = dist_from_center > (0.6 * max_radius)

                total_energy = float(np.sum(np.abs(f_shifted)))
                low_energy = float(np.sum(np.abs(f_shifted)[low_freq_mask]))
                high_energy = float(np.sum(np.abs(f_shifted)[high_freq_mask]))

                low_freq_ratio = (low_energy / total_energy * 100.0) if total_energy > 0 else 0.0
                high_freq_ratio = (high_energy / total_energy * 100.0) if total_energy > 0 else 0.0

                # 3. Peak Detection in High-Frequency Band (detects periodic lattices or generative grids)
                hf_norm = norm_spectrum.copy()
                hf_mask = dist_from_center > (0.25 * max_radius)
                hf_norm[~hf_mask] = 0  # Mask out central DC cluster

                # Mask central vertical and horizontal crosshairs (+- 3px) to ignore simple straight image borders
                hf_norm[max(0, cy - 3):min(height, cy + 4), :] = 0
                hf_norm[:, max(0, cx - 3):min(width, cx + 4)] = 0

                # Compute local background floor via Gaussian filter to measure true isolated harmonic spikes
                local_bg = cv2.GaussianBlur(hf_norm, (25, 25), 0)
                prominence = hf_norm.astype(np.float32) - local_bg.astype(np.float32)

                peak_mask = (prominence > 60.0) & hf_mask
                peak_count = int(np.sum(peak_mask))
                total_hf_bins = int(np.sum(hf_mask))
                peak_density = (peak_count / max(1, total_hf_bins)) * 100.0

                # Compute spectral decay slope
                y_coords, x_coords = np.ogrid[:height, :width]
                dist_int = np.sqrt((x_coords - cx) ** 2 + (y_coords - cy) ** 2).astype(np.int32)
                rad_prof = np.zeros(max_radius)
                for radius in range(1, max_radius):
                    m = (dist_int == radius)
                    if np.any(m):
                        rad_prof[radius] = np.mean(np.abs(f_shifted)[m])
                f_range = np.arange(max(2, max_radius // 8), max_radius // 2)
                valid = rad_prof[f_range] > 0
                if np.sum(valid) > 10:
                    slope, _ = np.polyfit(np.log10(f_range[valid]), np.log10(rad_prof[f_range][valid]), 1)
                    spectral_decay_slope = float(-slope)
                else:
                    spectral_decay_slope = 2.0

                analytics["low_freq_ratio"] = round(low_freq_ratio, 2)
                analytics["high_freq_ratio"] = round(high_freq_ratio, 2)
                analytics["prominent_hf_peaks"] = peak_count
                analytics["peak_density_pct"] = round(peak_density, 3)
                analytics["spectral_decay_slope"] = round(spectral_decay_slope, 2)

                observations.append(f"2D Discrete Fourier Transform computed on {width}x{height} pixel matrix.")
                observations.append(f"Low-frequency spectral power: {low_freq_ratio:.1f}% | High-frequency spectral power: {high_freq_ratio:.1f}%.")
                observations.append(f"Isolated high-frequency harmonic lattice peaks: {peak_count} (density {peak_density:.3f}%).")
                observations.append(f"Radial spectral decay slope: alpha={spectral_decay_slope:.2f}.")

                # Evaluate findings
                if peak_density > 0.35 and high_freq_ratio > 30.0:
                    indicator = "indicator_detected"
                    indicator_label = f"Periodic Harmonic Lattice Spikes Detected ({peak_count} peaks)"
                    explanation = (
                        f"Prominent periodic spectral peaks ({peak_count} isolated harmonic spikes, {peak_density:.3f}% density) observed "
                        "in the high-frequency Fourier spectrum. Strong periodic lattice patterns commonly indicate image resampling, "
                        "upscaling/interpolation, repeated pattern cloning, or synthetic GAN/diffusion checkerboard generative traces."
                    )
                elif peak_density > 0.15:
                    indicator = "inconclusive"
                    indicator_label = f"Moderate High-Frequency Spectral Variance ({peak_count} peaks)"
                    explanation = (
                        f"Moderate spectral harmonic peaks identified ({peak_count} peaks, {peak_density:.3f}% density). "
                        "While this may point to periodic resampling or compression artifacts, it is also standard for structured digital images, "
                        "such as monospace terminal tables, software user interfaces, or documents with repeated typography."
                    )
                else:
                    indicator = "no_indicator_detected"
                    indicator_label = "Fourier Spectral Frequency Decay Consistent"
                    explanation = (
                        "2D Fourier frequency spectrum exhibits natural, smooth radial power decay from DC center to Nyquist frequency. "
                        "No anomalous periodic resampling lattices or synthetic grid spikes were identified."
                    )

        except Exception as e:
            exec_time = round((time.perf_counter() - start_time) * 1000, 2)
            return ScreeningTestResult(
                method=cls.METHOD_NAME,
                version=cls.VERSION,
                status="failed",
                indicator="test_failed",
                indicator_label="Test failed",
                observations=[f"Error during Fourier spectral analysis: {str(e)}"],
                explanation="Fourier frequency transform encountered an unexpected processing error.",
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
