import time
from pathlib import Path
from typing import Dict, Any, List, Tuple
from PIL import Image
import numpy as np
import cv2

from app.core.config import settings
from app.schemas.examination import ScreeningTestResult


class CopyMoveAnalyzer:
    METHOD_NAME = "copy_move_forgery_detection"
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
            "Feature-based copy-move detection identifies duplicated textures; identical digital elements (icons, repeated font glyphs, table borders) naturally produce keypoint matches.",
            "Heavily blurred, smoothed, or compressed cloned regions may not retain sufficient corner features for keypoint extraction.",
            "Findings require examiner corroboration to distinguish fraudulent content duplication from legitimate graphic repetition."
        ]

        try:
            with Image.open(image_path) as img:
                rgb = np.array(img.convert("RGB"))
                gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
                height, width = gray.shape

                # 1. Feature Detection (ORB - Oriented FAST and Rotated BRIEF)
                orb = cv2.ORB_create(nfeatures=1200, scaleFactor=1.2, nlevels=4, edgeThreshold=15)
                keypoints, descriptors = orb.detectAndCompute(gray, None)

                num_keypoints = len(keypoints) if keypoints is not None else 0
                observations.append(f"Extracted {num_keypoints} interest keypoints across image matrix.")

                cloned_clusters = 0
                match_pairs: List[Tuple[Any, Any]] = []

                if descriptors is not None and len(descriptors) > 20:
                    # 2. Descriptors matching using Brute Force with Hamming distance
                    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=False)
                    # k=5 nearest neighbors to evaluate multiple candidate cloned regions
                    matches = bf.knnMatch(descriptors, descriptors, k=min(5, len(descriptors)))

                    # 3. Filter matches by descriptor distance & spatial separation
                    # Discard matches too close to each other (spatial distance < 45 px)
                    candidate_pairs = []
                    min_spatial_dist = 45.0

                    for match_list in matches:
                        if not match_list:
                            continue
                        query_idx = match_list[0].queryIdx
                        pt1 = keypoints[query_idx].pt

                        for m in match_list[1:]:  # Skip m[0] because it's matching itself (distance=0)
                            train_idx = m.trainIdx
                            if query_idx >= train_idx:
                                continue  # Avoid duplicate undirected pairs

                            pt2 = keypoints[train_idx].pt
                            dx = pt2[0] - pt1[0]
                            dy = pt2[1] - pt1[1]
                            spatial_dist = np.sqrt(dx ** 2 + dy ** 2)

                            # Hamming distance threshold (< 45 bits difference) and spatial separation
                            if m.distance < 45 and spatial_dist > min_spatial_dist:
                                candidate_pairs.append({
                                    "pt1": pt1,
                                    "pt2": pt2,
                                    "dx": dx,
                                    "dy": dy,
                                    "dist": spatial_dist,
                                    "angle": np.arctan2(dy, dx),
                                    "hamming": m.distance,
                                })

                    # 4. Cluster similar displacement vectors (indicates coherent cloned block translation)
                    if candidate_pairs:
                        # Group into spatial displacement bins (tolerance +- 15 px, +- 15 degrees)
                        clusters: Dict[int, List[Dict[str, Any]]] = {}
                        cluster_id = 0

                        for p in candidate_pairs:
                            assigned = False
                            for cid, members in clusters.items():
                                ref = members[0]
                                diff_dist = abs(p["dist"] - ref["dist"])
                                diff_angle = abs(p["angle"] - ref["angle"])
                                if diff_dist < 18.0 and diff_angle < 0.25:  # ~14 degrees
                                    members.append(p)
                                    assigned = True
                                    break
                            if not assigned:
                                clusters[cluster_id] = [p]
                                cluster_id += 1

                        # Find clusters with sufficient coherent matches
                        significant_clusters = [m for m in clusters.values() if len(m) >= 6]
                        cloned_clusters = len(significant_clusters)

                        # Flatten matching points and generate cluster regions
                        cluster_records = []
                        for cl in significant_clusters:
                            for item in cl:
                                match_pairs.append((item["pt1"], item["pt2"]))
                            src_xs = [int(p["pt1"][0]) for p in cl]
                            src_ys = [int(p["pt1"][1]) for p in cl]
                            cluster_records.append({
                                "src_x": max(0, min(src_xs) - 16),
                                "src_y": max(0, min(src_ys) - 16),
                                "w": max(src_xs) - min(src_xs) + 32,
                                "h": max(src_ys) - min(src_ys) + 32,
                                "count": len(cl),
                            })

                analytics["keypoints_extracted"] = num_keypoints
                analytics["candidate_match_pairs"] = len(match_pairs)
                analytics["matches_found"] = len(match_pairs)
                analytics["coherent_cloned_clusters"] = cloned_clusters
                analytics["clusters"] = cluster_records if 'cluster_records' in locals() else []

                # 5. Generate Visual Laboratory Artifact
                vis_img = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)

                if match_pairs:
                    # Draw connection lines between matched cloned patches
                    for p1, p2 in match_pairs[:100]:  # Cap at 100 lines for clarity
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

                # Evaluate findings
                if cloned_clusters >= 2 and len(match_pairs) >= 12:
                    indicator = "indicator_detected"
                    indicator_label = "Indicator detected"
                    explanation = (
                        f"Detected {cloned_clusters} coherent spatial displacement clusters containing {len(match_pairs)} "
                        "matching feature pairs. This pattern strongly indicates localized copy-move duplication (cloning of elements "
                        "from one portion of the image to another to replicate or obscure content)."
                    )
                elif len(match_pairs) > 4:
                    indicator = "inconclusive"
                    indicator_label = "Inconclusive"
                    explanation = (
                        f"Isolated feature matches observed ({len(match_pairs)} pairs), but without strong coherent displacement clustering. "
                        "This commonly occurs with repetitive digital graphics, identical font glyphs, or grid layouts. Manual verification recommended."
                    )
                else:
                    indicator = "no_indicator_detected"
                    indicator_label = "No indicator detected by this test"
                    explanation = (
                        "No coherent copy-move or cloned region clusters were detected. Feature descriptors across spatially separated "
                        "regions exhibit natural statistical variance."
                    )

        except Exception as e:
            exec_time = round((time.perf_counter() - start_time) * 1000, 2)
            return ScreeningTestResult(
                method=cls.METHOD_NAME,
                version=cls.VERSION,
                status="failed",
                indicator="test_failed",
                indicator_label="Test failed",
                observations=[f"Error during copy-move analysis: {str(e)}"],
                explanation="Copy-move forgery detection encountered an unexpected error.",
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
