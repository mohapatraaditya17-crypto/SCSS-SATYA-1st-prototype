import time
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional
from PIL import Image
import numpy as np
import cv2

from app.core.config import settings
from app.schemas.examination import ScreeningTestResult, DetectorResult, DetectorStatus, EvidenceStrength, EvidenceRegion


class CopyMoveAnalyzer:
    METHOD_NAME = "copy_move_forgery_detection"
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
            "Feature-based copy-move detection identifies duplicated textures; identical digital elements (icons, repeated font glyphs, table borders) naturally produce keypoint matches.",
            "Heavily blurred, smoothed, or compressed cloned regions may not retain sufficient corner features for keypoint extraction.",
            "Findings require examiner corroboration to distinguish fraudulent content duplication from legitimate graphic repetition."
        ]

        try:
            with Image.open(image_path) as img:
                rgb = np.array(img.convert("RGB"))
                gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
                height, width = gray.shape

                # 1. Feature Detection (ORB with enhanced feature budget)
                orb = cv2.ORB_create(nfeatures=1600, scaleFactor=1.2, nlevels=5, edgeThreshold=15)
                keypoints, descriptors = orb.detectAndCompute(gray, None)

                num_keypoints = len(keypoints) if keypoints is not None else 0
                observations.append(f"Extracted {num_keypoints} interest keypoints across image matrix.")

                cloned_clusters = 0
                match_pairs: List[Tuple[Any, Any]] = []
                cluster_records: List[Dict[str, Any]] = []

                if descriptors is not None and len(descriptors) > 20:
                    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=False)
                    matches = bf.knnMatch(descriptors, descriptors, k=min(6, len(descriptors)))

                    candidate_pairs = []
                    min_spatial_dist = 40.0

                    for match_list in matches:
                        if not match_list:
                            continue
                        query_idx = match_list[0].queryIdx
                        pt1 = keypoints[query_idx].pt

                        for m in match_list[1:]:
                            train_idx = m.trainIdx
                            if query_idx >= train_idx:
                                continue

                            pt2 = keypoints[train_idx].pt
                            dx = pt2[0] - pt1[0]
                            dy = pt2[1] - pt1[1]
                            spatial_dist = np.sqrt(dx ** 2 + dy ** 2)

                            # Hamming distance threshold (< 42 bits difference) and spatial separation
                            if m.distance < 42 and spatial_dist > min_spatial_dist:
                                candidate_pairs.append({
                                    "pt1": pt1,
                                    "pt2": pt2,
                                    "dx": dx,
                                    "dy": dy,
                                    "dist": spatial_dist,
                                    "angle": np.arctan2(dy, dx),
                                    "hamming": m.distance,
                                })

                    # Spatial displacement vector clustering
                    if candidate_pairs:
                        clusters: Dict[int, List[Dict[str, Any]]] = {}
                        cluster_id = 0

                        for p in candidate_pairs:
                            assigned = False
                            for cid, members in clusters.items():
                                ref = members[0]
                                diff_dist = abs(p["dist"] - ref["dist"])
                                diff_angle = abs(p["angle"] - ref["angle"])
                                if diff_dist < 22.0 and diff_angle < 0.30:  # ~17 degrees
                                    members.append(p)
                                    assigned = True
                                    break
                            if not assigned:
                                clusters[cluster_id] = [p]
                                cluster_id += 1

                        # In SATYA v2: A coherent single-paste operation produces >= 1 cluster of >= 6 matching points
                        significant_clusters = [m for m in clusters.values() if len(m) >= 5]
                        cloned_clusters = len(significant_clusters)

                        for cl in significant_clusters:
                            for item in cl:
                                match_pairs.append((item["pt1"], item["pt2"]))
                            src_xs = [int(p["pt1"][0]) for p in cl] + [int(p["pt2"][0]) for p in cl]
                            src_ys = [int(p["pt1"][1]) for p in cl] + [int(p["pt2"][1]) for p in cl]
                            rx = max(0, min(src_xs) - 16)
                            ry = max(0, min(src_ys) - 16)
                            rw = max(src_xs) - min(src_xs) + 32
                            rh = max(src_ys) - min(src_ys) + 32
                            cluster_records.append({
                                "src_x": rx,
                                "src_y": ry,
                                "w": rw,
                                "h": rh,
                                "count": len(cl),
                            })
                            affected_regions.append(
                                EvidenceRegion(
                                    x=rx,
                                    y=ry,
                                    width=rw,
                                    height=rh,
                                    confidence=round(min(0.95, 0.70 + (len(cl) * 0.03)), 2),
                                    detector=cls.METHOD_NAME,
                                    label=f"Cloned / Duplicated Keypoint Cluster ({len(cl)} pairs)",
                                )
                            )

                analytics["keypoints_extracted"] = num_keypoints
                analytics["candidate_match_pairs"] = len(match_pairs)
                analytics["matches_found"] = len(match_pairs)
                analytics["coherent_cloned_clusters"] = cloned_clusters
                analytics["clusters"] = cluster_records

                # Generate Visual Artifact
                vis_img = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
                if match_pairs:
                    for p1, p2 in match_pairs[:120]:
                        pt1_int = (int(p1[0]), int(p1[1]))
                        pt2_int = (int(p2[0]), int(p2[1]))
                        cv2.circle(vis_img, pt1_int, 4, (0, 0, 255), -1)
                        cv2.circle(vis_img, pt2_int, 4, (255, 165, 0), -1)
                        cv2.line(vis_img, pt1_int, pt2_int, (0, 255, 255), 1, cv2.LINE_AA)

                artifact_filename = f"{examination_id}_copymove.png"
                artifact_path = settings.ARTIFACTS_DIR / artifact_filename
                cv2.imwrite(str(artifact_path), vis_img)
                artifacts["copymove_map"] = artifact_filename

                observations.append(f"Identified {len(match_pairs)} spatially-separated descriptor match candidates.")
                observations.append(f"Coherent vector translation clusters identified: {cloned_clusters}.")

                # Calibrated decision threshold in SATYA v2
                # Cloned cluster >= 1 with >= 6 coherent pairs indicates copy-move
                if cloned_clusters >= 1 and len(match_pairs) >= 6:
                    indicator = "indicator_detected"
                    indicator_label = "Indicator detected"
                    norm_status = DetectorStatus.POSITIVE.value
                    score = min(0.96, 0.75 + (cloned_clusters * 0.08) + (len(match_pairs) * 0.01))
                    confidence = 0.90
                    strength = EvidenceStrength.STRONG.value
                    explanation = (
                        f"Detected {cloned_clusters} coherent spatial displacement cluster(s) containing {len(match_pairs)} "
                        "matching feature pairs. This pattern strongly indicates localized copy-move duplication (cloning of elements "
                        "from one portion of the image to another to replicate or obscure content)."
                    )
                elif len(match_pairs) >= 3:
                    indicator = "inconclusive"
                    indicator_label = "Inconclusive"
                    norm_status = DetectorStatus.INCONCLUSIVE.value
                    score = 0.35
                    confidence = 0.50
                    strength = EvidenceStrength.LOW.value
                    explanation = (
                        f"Isolated feature matches observed ({len(match_pairs)} pairs), but without strong coherent displacement clustering. "
                        "This commonly occurs with repetitive digital graphics, identical font glyphs, or grid layouts. Manual verification recommended."
                    )
                else:
                    indicator = "no_indicator_detected"
                    indicator_label = "No indicator detected by this test"
                    norm_status = DetectorStatus.NEGATIVE.value
                    score = 0.05
                    confidence = 0.85
                    strength = EvidenceStrength.NONE.value
                    explanation = (
                        "No coherent copy-move or cloned region clusters were detected. Feature descriptors across spatially separated "
                        "regions exhibit natural statistical variance."
                    )

        except Exception as e:
            exec_time = round((time.perf_counter() - start_time) * 1000, 2)
            res = ScreeningTestResult(
                method=cls.METHOD_NAME,
                version=cls.VERSION,
                status="failed",
                indicator="test_failed",
                indicator_label="Test failed",
                observations=[f"Error during copy-move analysis: {str(e)}"],
                explanation="Copy-move forgery detection encountered an unexpected error.",
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
