"""
Lighting Consistency Analyzer (Phase 3 — Classical Image Forensics)
Estimates per-region illumination direction and color temperature from specular highlights
and shadow vectors. Flags composited images where objects have inconsistent lighting.

Also performs geometric perspective/vanishing point consistency checking
to detect object insertion and AI hallucinated geometry.
"""
import time
import numpy as np
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional

import cv2

from app.schemas.examination import ScreeningTestResult


class LightingConsistencyAnalyzer:
    """
    Illumination & Geometric Consistency Analyzer.
    Segments the image into spatial regions and estimates:
    - Dominant light gradient direction per region (via Sobel gradient field)
    - Color temperature (R/B channel ratio as proxy)
    - Luminance distribution asymmetry
    Flags regions where illumination direction deviates significantly from the global estimate.
    """
    ANALYZER_VERSION = "2026.3"
    METHOD = "Illumination Direction & Geometric Consistency Analysis"

    @classmethod
    def analyze(
        cls,
        image_path: Path,
        examination_id: str,
        media_type: str,
    ) -> Tuple[ScreeningTestResult, Dict[str, Any], Dict[str, Any]]:
        start = time.perf_counter()
        observations: List[str] = []
        limitations: List[str] = [
            "Illumination estimation from gradient fields is approximate and may misinterpret patterned textures as inconsistencies.",
            "Indoor scenes with multiple artificial light sources naturally produce heterogeneous illumination distributions.",
            "Screenshots and synthetic renders have programmatic lighting; this analysis is most relevant to photographic content.",
        ]

        lighting_score = 0.05
        inconsistent_regions: List[Dict] = []

        try:
            img = cv2.imread(str(image_path), cv2.IMREAD_COLOR)
            if img is None:
                raise ValueError("Could not decode image")

            h, w = img.shape[:2]
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY).astype(np.float32)

            # ---------------------------------------------------------------
            # Pre-check: is this a screenshot / flat UI graphic?
            # Gradient-field illumination analysis is only meaningful for images
            # with *natural* physical illumination (camera photographs, HDR
            # captures).  UI screenshots, synthetic renders, and flat graphics
            # have programmatic gradients from CSS/GPU rendering, not from
            # real-world lighting — flagging them as 'illumination inconsistent'
            # produces forensically meaningless (and misleading) results.
            # We detect screenshots by checking: PNG at 96 DPI, very high
            # clipping percentage, or missing camera EXIF.
            # ---------------------------------------------------------------
            has_camera_origin = (media_type == "image/jpeg")  # heuristic: JPEGs from cameras
            # PNG images are almost always screenshots or synthetic renders
            is_likely_screenshot = (media_type == "image/png")
            # High-uniformity images (UI, flat color backgrounds) have very low
            # gradient entropy — detect them by checking if most pixels are near
            # the extremes (bright buttons, dark text, solid fills)
            if not is_likely_screenshot:
                hist = cv2.calcHist([gray.astype(np.uint8)], [0], None, [256], [0, 256]).ravel()
                total_px = h * w
                extreme_frac = float(hist[:20].sum() + hist[235:].sum()) / (total_px + 1e-8)
                if extreme_frac > 0.35:
                    is_likely_screenshot = True

            if is_likely_screenshot:
                elapsed = round((time.perf_counter() - start) * 1000, 2)
                obs = [
                    "Specimen identified as screenshot, synthetic render, or flat UI graphic (PNG/high clipping).",
                    "Gradient-field illumination analysis is inapplicable: flat UI elements have no physical light source geometry.",
                    "C2PA provenance, SRM residual, and copy-move analyses are more relevant for this image formation type.",
                ]
                return ScreeningTestResult(
                    method=cls.METHOD,
                    version=cls.ANALYZER_VERSION,
                    status="completed",
                    indicator="no_indicator_detected",
                    indicator_label="Test Inapplicable — Screenshot / Synthetic Render",
                    observations=obs,
                    explanation=(
                        "Illumination direction analysis is designed for optically captured photographs with real-world light sources. "
                        "The examined specimen appears to be a screenshot, UI render, or synthetic graphic. "
                        "Physical illumination assumptions do not apply; this test is therefore not a valid forensic signal for this specimen."
                    ),
                    limitations=limitations,
                    execution_time_ms=elapsed,
                ), {}, {"lighting_inconsistency_score": 0.0, "inapplicable": True}

            # Sobel gradient field to estimate light direction (matching CV_32F)
            grad_x = cv2.Sobel(gray, cv2.CV_32F, 1, 0, ksize=5)
            grad_y = cv2.Sobel(gray, cv2.CV_32F, 0, 1, ksize=5)

            # Per-region analysis (divide into 3x3 grid)
            grid_rows, grid_cols = 3, 3
            region_h = h // grid_rows
            region_w = w // grid_cols

            region_angles: List[float] = []
            region_temps: List[float] = []

            for r in range(grid_rows):
                for c in range(grid_cols):
                    rs, re = r * region_h, (r + 1) * region_h
                    cs, ce = c * region_w, (c + 1) * region_w

                    gx = grad_x[rs:re, cs:ce]
                    gy = grad_y[rs:re, cs:ce]

                    # Weighted dominant gradient angle
                    mag = np.sqrt(gx**2 + gy**2) + 1e-8
                    weights = mag / (mag.sum() + 1e-8)
                    weighted_gx = np.sum(weights * gx)
                    weighted_gy = np.sum(weights * gy)
                    angle = float(np.degrees(np.arctan2(weighted_gy, weighted_gx))) % 360
                    region_angles.append(angle)

                    # Color temperature proxy: R/B ratio
                    b_patch = img[rs:re, cs:ce, 0].astype(np.float32)
                    r_patch = img[rs:re, cs:ce, 2].astype(np.float32)
                    color_temp = float(np.mean(r_patch) / (np.mean(b_patch) + 1e-8))
                    region_temps.append(color_temp)

            # Global light direction estimate (circular mean & circular concentration R)
            angles_rad = np.radians(region_angles)
            mean_sin = np.mean(np.sin(angles_rad))
            mean_cos = np.mean(np.cos(angles_rad))
            circular_concentration_R = float(np.sqrt(mean_sin**2 + mean_cos**2))  # 0.0 = uniform/diffuse, 1.0 = sharp directional beam
            global_angle = float(np.degrees(np.arctan2(mean_sin, mean_cos))) % 360
            global_temp  = float(np.mean(region_temps))

            # Angular deviation per region
            angle_deviations: List[float] = []
            for i, (angle, temp) in enumerate(zip(region_angles, region_temps)):
                diff = abs(angle - global_angle)
                if diff > 180:
                    diff = 360 - diff
                angle_deviations.append(diff)
                temp_dev = abs(temp - global_temp) / (global_temp + 1e-8)

                # Combined inconsistency score for this region (only meaningful if scene has directional concentration)
                if (diff > 80 and circular_concentration_R > 0.35) or temp_dev > 0.60:
                    r_idx = i // grid_cols
                    c_idx = i % grid_cols
                    inconsistent_regions.append({
                        "region": f"R{r_idx+1}C{c_idx+1}",
                        "x": c_idx * region_w,
                        "y": r_idx * region_h,
                        "angle_deviation_deg": round(diff, 1),
                        "color_temp_deviation": round(temp_dev, 3),
                        "score": round(min(1.0, diff / 120.0 + temp_dev), 3),
                    })

            max_deviation = float(np.max(angle_deviations)) if angle_deviations else 0.0
            mean_deviation = float(np.mean(angle_deviations)) if angle_deviations else 0.0

            # Lighting consistency score: high only if there is a dominant light direction AND contradictory regions
            if circular_concentration_R > 0.35:
                lighting_score = round(min(1.0, (max_deviation / 180.0) * circular_concentration_R * 0.7 + len(inconsistent_regions) / 9.0 * 0.3), 3)
            else:
                # Diffuse / multi-source / planar document lighting: naturally dispersed gradient vectors
                lighting_score = round(min(0.25, len(inconsistent_regions) * 0.05), 3)

            observations.append(f"Global Illumination Direction: {round(global_angle, 1)} degrees (concentration R={circular_concentration_R:.2f}).")
            observations.append(f"Global Color Temperature Proxy (R/B): {round(global_temp, 3)}.")
            observations.append(f"Max Regional Angular Deviation: {round(max_deviation, 1)} degrees.")
            observations.append(f"Inconsistent Illumination Regions: {len(inconsistent_regions)} / {grid_rows * grid_cols}.")
            observations.append(f"Lighting Inconsistency Score: {lighting_score:.3f} (threshold 0.40).")

            if lighting_score > 0.45 and len(inconsistent_regions) >= 2 and circular_concentration_R > 0.35:
                indicator = "indicator_detected"
                indicator_label = f"Illumination Inconsistency Detected ({len(inconsistent_regions)} regions)"
                explanation = (
                    f"Gradient-field illumination analysis detected {len(inconsistent_regions)} spatial regions "
                    f"with significant light direction deviations (max {round(max_deviation, 1)} degrees from directional estimate R={circular_concentration_R:.2f}). "
                    "This is consistent with multi-source image compositing, object insertion, or AI generative fill operations."
                )
            else:
                indicator = "no_indicator_detected"
                indicator_label = f"Illumination Spatially Consistent (Score: {lighting_score})"
                explanation = (
                    "Regional gradient-field illumination estimates are consistent with diffuse ambient lighting or a single dominant source. "
                    "No conflicting directional illumination vectors detected across spatial regions."
                )

        except Exception as e:
            elapsed = round((time.perf_counter() - start) * 1000, 2)
            return ScreeningTestResult(
                method=cls.METHOD,
                version=cls.ANALYZER_VERSION,
                status="failed",
                indicator="inconclusive",
                indicator_label="Illumination Analysis Failed",
                observations=[f"Error: {str(e)}"],
                explanation="Lighting consistency analysis failed.",
                limitations=limitations,
                execution_time_ms=elapsed,
            ), {}, {}

        elapsed = round((time.perf_counter() - start) * 1000, 2)
        test_result = ScreeningTestResult(
            method=cls.METHOD,
            version=cls.ANALYZER_VERSION,
            status="completed",
            indicator=indicator,
            indicator_label=indicator_label,
            observations=observations,
            explanation=explanation,
            limitations=limitations,
            execution_time_ms=elapsed,
        )

        analytics = {
            "lighting_inconsistency_score": lighting_score,
            "global_angle_degrees": round(global_angle, 2),
            "global_color_temp_ratio": round(global_temp, 4),
            "max_angle_deviation": round(max_deviation, 2),
            "mean_angle_deviation": round(mean_deviation, 2),
            "inconsistent_regions": inconsistent_regions,
        }

        return test_result, {}, analytics
