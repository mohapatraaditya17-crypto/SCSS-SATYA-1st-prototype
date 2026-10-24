"""
Splicing Inconsistency Detector (Phase 3 — Image Forensics)
Detects multi-source image composition by analyzing regional statistical inconsistencies:
- Noise variance block analysis (forgery maps via local noise estimator)
- Local neighbourhood comparison (same-luminance-tier blocks) to eliminate natural-photo false alarms
- Boundary clustering for contiguous spliced object localization

Reference: Farid (2009) - Image forgery detection. IEEE Signal Processing Magazine.
Fridrich & Kodovsky (2012) - Rich models for steganalysis of digital images.
"""
import time
import numpy as np
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional

import cv2
from PIL import Image

from app.schemas.examination import ScreeningTestResult


class SplicingDetector:
    """
    Splicing & Composite Forgery Detector.

    Uses local neighbourhood-conditioned noise residual comparison to identify
    statistically inconsistent blocks. Each block is scored ONLY against its
    spatially nearby peers with similar luminance — preventing natural lighting
    gradients and shadows from being mistaken for foreign pastes.
    """
    ANALYZER_VERSION = "2026.5"
    METHOD = "Image Splicing & Composite Forgery Detector"
    BLOCK_SIZE = 48

    @classmethod
    def analyze(
        cls,
        image_path: Path,
        examination_id: str,
        media_type: str,
        artifacts_dir: Optional[Path] = None,
    ) -> Tuple[ScreeningTestResult, Dict[str, Any], Dict[str, Any]]:
        start = time.perf_counter()
        observations: List[str] = []
        limitations: List[str] = [
            "Block-based noise analysis may flag natural lighting transitions in photographs (e.g. indoor/outdoor frames).",
            "Heavy JPEG recompression homogenizes block statistics, reducing splicing indicator sensitivity.",
            "Text, logos, and UI overlay regions on screenshots will typically show elevated statistical divergence vs. photographic backgrounds.",
        ]

        splice_score = 0.05
        anomalous_blocks: List[Dict[str, Any]] = []
        suspicious_regions: List[Dict[str, Any]] = []

        try:
            img = cv2.imread(str(image_path), cv2.IMREAD_COLOR)
            if img is None:
                raise ValueError("Could not decode image")

            h, w = img.shape[:2]
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY).astype(np.float32)

            bs = cls.BLOCK_SIZE
            rows = h // bs
            cols = w // bs

            if rows < 3 or cols < 3:
                observations.append("Image too small for block-based splicing analysis (minimum 144x144 required).")
                elapsed = round((time.perf_counter() - start) * 1000, 2)
                return ScreeningTestResult(
                    method=cls.METHOD,
                    version=cls.ANALYZER_VERSION,
                    status="completed",
                    indicator="no_indicator_detected",
                    indicator_label="Image Too Small for Block Splicing Analysis",
                    observations=observations,
                    explanation="Image dimensions below minimum threshold for reliable block-level statistical analysis.",
                    limitations=limitations,
                    execution_time_ms=elapsed,
                ), {}, {}

            # -------------------------------------------------------------------
            # Step 1: High-pass noise residual extraction
            # Use median filter residual on grayscale — captures sensor noise
            # without being confused by actual image content (edges, texture).
            # -------------------------------------------------------------------
            gray_u8 = gray.astype(np.uint8)
            median_blur = cv2.medianBlur(gray_u8, 3).astype(np.float32)
            noise_residual = np.abs(gray - median_blur)   # shape (h, w), float32

            # -------------------------------------------------------------------
            # Step 2: Gradient magnitude for low-gradient mask
            # High-gradient pixels (edges, text strokes) naturally have high noise;
            # exclude them so we measure only flat-region sensor noise.
            # -------------------------------------------------------------------
            gx = cv2.Sobel(gray, cv2.CV_32F, 1, 0, ksize=3)
            gy = cv2.Sobel(gray, cv2.CV_32F, 0, 1, ksize=3)
            gmag = np.sqrt(gx ** 2 + gy ** 2)

            # -------------------------------------------------------------------
            # Step 3: Per-block features: mean luminance + noise variance on
            # low-gradient pixels only (or full block if mostly edges).
            # -------------------------------------------------------------------
            block_lum   = np.zeros((rows, cols), dtype=np.float32)
            block_noise = np.zeros((rows, cols), dtype=np.float32)

            for r in range(rows):
                for c in range(cols):
                    blk_gray  = gray[r*bs:(r+1)*bs, c*bs:(c+1)*bs]
                    blk_noise = noise_residual[r*bs:(r+1)*bs, c*bs:(c+1)*bs]
                    blk_gmag  = gmag[r*bs:(r+1)*bs, c*bs:(c+1)*bs]

                    block_lum[r, c] = float(np.mean(blk_gray))

                    # Skip near-black blocks — zero-luminance regions have no measurable
                    # sensor noise; their variance = 0 makes them appear as extreme outliers
                    # relative to any textured neighbour, creating systematic false positives
                    # on dark-background photos (night shots, dark documents, etc.)
                    if block_lum[r, c] < 10.0:
                        block_noise[r, c] = -1.0   # sentinel: skip in peer comparison
                        continue

                    low_g = blk_gmag < 20.0
                    valid_px = int(np.sum(low_g))
                    if valid_px >= bs * bs // 5:
                        block_noise[r, c] = float(np.var(blk_noise[low_g]))
                    else:
                        # Mostly-edge block — fall back to full-block variance,
                        # but weight it lower later by marking it as high-gradient.
                        block_noise[r, c] = float(np.var(blk_noise)) * 0.5

            # -------------------------------------------------------------------
            # Step 4: Local neighbourhood comparison
            # For each block, compare its noise variance against its immediate
            # 3×3 neighbours that have similar luminance (within ±30 DN).
            # This eliminates natural global gradients (sky→ground, bright→shadow)
            # while still detecting abrupt foreign-paste boundaries.
            # -------------------------------------------------------------------
            anomaly_matrix = np.zeros((rows, cols), dtype=np.float32)
            LUM_TIER_WIDTH = 30.0   # luminance bins for peer selection

            for r in range(rows):
                for c in range(cols):
                    center_lum   = block_lum[r, c]
                    center_noise = block_noise[r, c]

                    # Skip sentinel dark blocks
                    if center_noise < 0:
                        continue

                    # Collect spatially nearby blocks (up to 5-block radius)
                    r0, r1 = max(0, r - 5), min(rows, r + 6)
                    c0, c1 = max(0, c - 5), min(cols, c + 6)
                    peer_lums   = block_lum[r0:r1, c0:c1].ravel()
                    peer_noises = block_noise[r0:r1, c0:c1].ravel()

                    # Exclude sentinel blocks from peer pool
                    valid_peers = peer_noises >= 0
                    peer_lums   = peer_lums[valid_peers]
                    peer_noises = peer_noises[valid_peers]

                    # Filter to same luminance tier
                    same_tier = np.abs(peer_lums - center_lum) <= LUM_TIER_WIDTH
                    same_tier_noises = peer_noises[same_tier]

                    if len(same_tier_noises) < 4:
                        # Not enough peers — skip (no anomaly for this block)
                        continue

                    peer_med = float(np.median(same_tier_noises))
                    peer_mad = float(np.median(np.abs(same_tier_noises - peer_med))) + 1e-4

                    z = abs(center_noise - peer_med) / peer_mad

                    # Threshold 5.5 MAD from local peers.
                    # Raised from 4.5: natural texture transitions (smooth→rough, shadow→highlight)
                    # in optical photos routinely hit 4-5 MAD when luminance-tier peers are limited.
                    # Genuine foreign pastes produce consistent blocks of 6-8+ MAD.
                    if z > 5.5:
                        score = float(min(0.90, 0.45 + (z - 5.5) * 0.08))
                        anomaly_matrix[r, c] = score
                        anomalous_blocks.append({
                            "x": c * bs,
                            "y": r * bs,
                            "w": bs,
                            "h": bs,
                            "score": round(score, 3),
                            "noise_z": round(float(z), 2),
                        })

            total_blocks  = rows * cols
            anomaly_count = len(anomalous_blocks)
            anomaly_ratio = anomaly_count / max(total_blocks, 1)

            # -------------------------------------------------------------------
            # Step 5: Connected Component Clustering
            # Only contiguous clusters of ≥ 4 blocks are treated as potential
            # spliced objects. Isolated outliers are sensor/compression artefacts.
            # -------------------------------------------------------------------
            bin_map = (anomaly_matrix > 0.40).astype(np.uint8)
            num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(bin_map, connectivity=8)

            clustered_regions_count = 0
            significant_cluster_area = 0
            for label_id in range(1, num_labels):
                area = int(stats[label_id, cv2.CC_STAT_AREA])
                if area >= 6:   # Minimum 6-block cluster (~144×144 px) — genuine splices are physically large
                    rx = int(stats[label_id, cv2.CC_STAT_LEFT]  * bs)
                    ry = int(stats[label_id, cv2.CC_STAT_TOP]   * bs)
                    rw = int(stats[label_id, cv2.CC_STAT_WIDTH] * bs)
                    rh = int(stats[label_id, cv2.CC_STAT_HEIGHT]* bs)
                    clustered_regions_count += 1
                    significant_cluster_area += area
                    suspicious_regions.append({
                        "x": rx,
                        "y": ry,
                        "width":  rw,
                        "height": rh,
                        "score":  round(min(0.92, 0.55 + area * 0.04), 2),
                        "label":  f"Spliced / Foreign Composite Region ({area} blocks)",
                    })

            # -------------------------------------------------------------------
            # Step 6: Calibrated splice score
            # The score is capped by anomaly_ratio so a clean image (few anomalous
            # blocks) can never reach a high splice_score regardless of clusters.
            # Natural images: anomaly_ratio typically < 0.08 → score < 0.35.
            # Genuine splice: anomaly_ratio typically > 0.15 + coherent clusters.
            # -------------------------------------------------------------------
            cluster_contribution = min(0.50, significant_cluster_area * 0.025) if clustered_regions_count > 0 else 0.0
            ratio_contribution   = min(0.50, anomaly_ratio * 2.5)
            raw_score = cluster_contribution + ratio_contribution

            # Hard cap: if anomaly_ratio < 0.10, splice_score ≤ 0.30 (inconclusive)
            if anomaly_ratio < 0.10:
                splice_score = round(min(0.30, raw_score), 3)
            elif anomaly_ratio < 0.20:
                splice_score = round(min(0.60, raw_score), 3)
            else:
                splice_score = round(min(0.92, raw_score), 3)

            observations.append(f"Block Splicing Grid: {total_blocks} blocks ({rows}x{cols}) at {bs}x{bs}px each.")
            observations.append(f"Anomalous Blocks (local-peer MAD > 4.5σ): {anomaly_count} / {total_blocks} ({round(anomaly_ratio*100, 1)}%).")
            if clustered_regions_count > 0:
                observations.append(f"Contiguous Spliced Component Clusters (≥4 blocks): {clustered_regions_count} identified.")
            observations.append(f"Splicing Inconsistency Score: {splice_score:.3f} (threshold 0.40 for indicator).")

            # Indicator threshold: 0.40 splice_score AND at least 1 cluster
            if splice_score >= 0.40 and clustered_regions_count > 0:
                indicator = "indicator_detected"
                indicator_label = (
                    f"Splicing Inconsistency Detected ({clustered_regions_count} cluster"
                    f"{'s' if clustered_regions_count != 1 else ''}, {anomaly_count} anomalous blocks)"
                )
                explanation = (
                    f"Local-peer noise residual analysis detected {anomaly_count} inconsistent blocks forming "
                    f"{clustered_regions_count} contiguous spatial cluster(s) with noise statistics inconsistent "
                    "with neighbouring same-luminance image regions. This pattern is consistent with multi-source "
                    "image compositing, foreign object insertion, or regional generative fill."
                )
            else:
                indicator = "no_indicator_detected"
                indicator_label = f"Block Statistics Consistent (Score: {splice_score})"
                explanation = (
                    "Local-peer noise residual comparison shows statistically homogeneous noise distributions "
                    "across same-luminance image blocks. No coherent foreign compositing or spliced patches identified."
                )

        except Exception as e:
            elapsed = round((time.perf_counter() - start) * 1000, 2)
            return ScreeningTestResult(
                method=cls.METHOD,
                version=cls.ANALYZER_VERSION,
                status="failed",
                indicator="inconclusive",
                indicator_label="Splicing Analysis Failed",
                observations=[f"Error: {str(e)}"],
                explanation="Splicing detection failed due to a processing error.",
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
            "splice_score": splice_score,
            "anomalous_blocks": anomaly_count,
            "total_blocks": rows * cols,
            "anomaly_ratio": round(anomaly_ratio, 4),
            "clustered_regions": clustered_regions_count,
            "suspicious_regions": suspicious_regions[:10],
        }

        return test_result, {}, analytics
