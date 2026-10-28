from pathlib import Path
from typing import List, Dict, Any, Optional
import cv2
import numpy as np

from app.core.config import settings
from app.schemas.examination import DetectorResult, EvidenceRegion


class CompositeHeatmapGenerator:
    """
    Forensic Evidence Heatmap & Region Fusion Engine.
    Combines multi-method localization cues (copy-move keypoint clusters,
    splicing boundary blocks, noise residual anomalies, ELA hot-spots) into
    a unified Composite Forensic Heatmap with evidence agreement highlighting.
    """
    VERSION = "2.0.0"

    @classmethod
    def generate(
        cls,
        image_path: Path,
        examination_id: str,
        detector_results: List[DetectorResult],
        all_artifacts: Dict[str, Any],
    ) -> Optional[str]:
        """
        Renders a composite evidence visualization where independent detector findings
        overlap in spatial coordinates.
        """
        try:
            img = cv2.imread(str(image_path), cv2.IMREAD_COLOR)
            if img is None:
                return None

            h, w = img.shape[:2]
            overlay = img.copy()
            density_map = np.zeros((h, w), dtype=np.float32)

            all_regions: List[EvidenceRegion] = []
            for res in detector_results:
                for reg in res.affected_regions:
                    all_regions.append(reg)

            # Draw regions onto density map and overlay
            for reg in all_regions:
                rx = max(0, min(w - 1, reg.x))
                ry = max(0, min(h - 1, reg.y))
                rw = max(16, min(w - rx, reg.width))
                rh = max(16, min(h - ry, reg.height))

                weight = float(reg.confidence) if reg.confidence > 0 else 0.8
                density_map[ry:ry + rh, rx:rx + rw] += weight

                # Bounding box color based on detector
                if "copy_move" in reg.detector:
                    color = (0, 255, 255)  # Yellow
                elif "splicing" in reg.detector:
                    color = (0, 0, 255)    # Red
                elif "typography" in reg.detector:
                    color = (255, 0, 255)  # Magenta
                else:
                    color = (0, 165, 255)  # Orange

                cv2.rectangle(overlay, (rx, ry), (rx + rw, ry + rh), color, 2)
                label_text = f"{reg.detector[:12]}: {round(weight * 100)}%"
                cv2.putText(
                    overlay, label_text, (rx + 4, max(16, ry - 6)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, color, 1, cv2.LINE_AA
                )

            # Apply colormap to density heatmap where multiple methods agree
            if np.max(density_map) > 0:
                norm_density = cv2.normalize(density_map, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)
                color_density = cv2.applyColorMap(norm_density, cv2.COLORMAP_JET)
                
                # Blend density map with overlay
                mask = (norm_density > 25).astype(np.uint8)[:, :, None]
                blended = cv2.addWeighted(overlay, 0.70, color_density, 0.30, 0)
                final_vis = np.where(mask > 0, blended, overlay)
            else:
                final_vis = overlay

            # Add Header Banner
            header_h = 36
            banner = np.zeros((header_h, w, 3), dtype=np.uint8)
            cv2.rectangle(banner, (0, 0), (w, header_h), (25, 25, 30), -1)
            cv2.putText(
                banner,
                f"SCSS SATYA v2 - Composite Evidence Heatmap (ID: {examination_id})",
                (12, 24),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.55,
                (0, 220, 255),
                1,
                cv2.LINE_AA,
            )

            stacked = np.vstack([banner, final_vis])

            composite_filename = f"{examination_id}_composite_evidence.png"
            out_path = settings.ARTIFACTS_DIR / composite_filename
            cv2.imwrite(str(out_path), stacked)
            return composite_filename

        except Exception:
            return None

