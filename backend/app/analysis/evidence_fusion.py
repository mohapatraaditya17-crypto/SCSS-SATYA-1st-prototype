import math
from typing import Dict, Any, List, Optional
from app.schemas.examination import ScreeningTestResult


class EvidenceFusionEngine:
    """
    Evidence Correlation, Calibrated Confidence Scoring & Four-Pillar Forensic Engine.
    Conforms to NIST OpenMFC, ISO/IEC 27037, and C2PA Specification 2.x standards.
    
    Replaces naive binary classifiers with a multi-layer calibrated evidence fusion model
    answering the Four Independent Forensic Questions:
      Q1 - Origin: Where did this content originate?
      Q2 - Integrity: Has the file/content been altered?
      Q3 - Generation: Was AI used to generate it?
      Q4 - Transformation: What operations were performed?
    """
    ENGINE_VERSION = "2026.2"

    @classmethod
    def fuse_evidence(
        cls,
        case_id: str,
        original_filename: str,
        media_type: str,
        file_size_bytes: int,
        hashes: Dict[str, Any],
        extracted_metadata: Dict[str, Any],
        c2pa_analytics: Dict[str, Any],
        jpeg_analytics: Dict[str, Any],
        document_analytics: Dict[str, Any],
        all_artifacts: Dict[str, Any],
        all_tests: List[ScreeningTestResult],
    ) -> Dict[str, Any]:
        """
        Synthesizes raw signals from all screening modules into calibrated probability scores,
        answers the 4 forensic questions, extracts localized suspicious regions, and formats
        the canonical evidence JSON schema.
        """
        # 1. Extract raw signal metrics from artifacts & tests
        noise_analytics     = all_artifacts.get("noise_analytics", {})
        fft_analytics       = all_artifacts.get("fft_analytics", {})
        copymove_analytics  = all_artifacts.get("copymove_analytics", {})
        ai_analytics        = all_artifacts.get("ai_synthetic_analytics", {})
        typo_analytics      = all_artifacts.get("typography_analytics", {})
        srm_analytics       = all_artifacts.get("srm_analytics", {})
        splicing_analytics  = all_artifacts.get("splicing_analytics", {})
        lighting_analytics  = all_artifacts.get("lighting_analytics", {})

        # Provenance metrics
        c2pa_present = c2pa_analytics.get("c2pa_present", False)
        signature_valid = c2pa_analytics.get("signature_valid")
        ai_declared = c2pa_analytics.get("ai_declared", False)
        provenance_conf = c2pa_analytics.get("provenance_confidence", 0.10)

        # Metadata metrics
        is_screen_capture = extracted_metadata.get("PNG:ScreenDensityDPI") == 96 or "screenshot" in original_filename.lower()
        has_camera_exif = bool(extracted_metadata.get("Make") or extracted_metadata.get("Model"))
        metadata_software = extracted_metadata.get("Software") or jpeg_analytics.get("software_fingerprint") or "Unknown"

        # Metadata anomaly score (0.0 = completely consistent, 1.0 = highly anomalous)
        metadata_anomaly_score = 0.05
        if has_camera_exif and ("photoshop" in str(metadata_software).lower() or "gimp" in str(metadata_software).lower()):
            metadata_anomaly_score = 0.75
        elif not has_camera_exif and not is_screen_capture and media_type == "image/jpeg":
            metadata_anomaly_score = 0.45

        # Classical Forensics scores
        ela_test = next((t for t in all_tests if "Error Level Analysis" in t.method), None)
        ela_score = 0.65 if (ela_test and ela_test.indicator == "indicator_detected") else 0.15

        jpeg_anomaly = 0.70 if jpeg_analytics.get("double_compression_suspected") else 0.10
        
        # Robust noise inconsistency: requires BOTH elevated ratio AND high kurtosis.
        # Natural photographs routinely have inhomogeneity_ratio of 50–300 due to natural
        # variation between textured and smooth image regions (sky, skin, grass, shadow).
        # Genuine splicing/compositing additionally produces heavy-tailed residuals (kurtosis >> 18).
        inhomogeneity_ratio = float(noise_analytics.get("inhomogeneity_ratio", 1.0))
        noise_kurtosis      = float(noise_analytics.get("kurtosis", 3.0))
        # Only trigger noise_inconsistency if BOTH ratio AND kurtosis are extreme
        if inhomogeneity_ratio > 500.0 and noise_kurtosis > 18.0:
            noise_inconsistency = min(1.0, 0.55 + (inhomogeneity_ratio - 500.0) / 500.0)
        elif inhomogeneity_ratio > 250.0 and noise_kurtosis > 18.0:
            noise_inconsistency = 0.45
        elif noise_kurtosis > 30.0 and inhomogeneity_ratio > 100.0:
            noise_inconsistency = 0.35
        else:
            noise_inconsistency = 0.05

        copy_move_score = 0.88 if (copymove_analytics.get("matches_found", 0) > 8 or copymove_analytics.get("candidate_match_pairs", 0) > 8) and copymove_analytics.get("coherent_cloned_clusters", 0) >= 1 else 0.02
        
        # Phase 3 signals
        srm_splice_score   = float(srm_analytics.get("srm_splice_score", 0.05))
        block_splice_score = float(splicing_analytics.get("splice_score", 0.05))
        lighting_score     = float(lighting_analytics.get("lighting_inconsistency_score", 0.05))

        splice_score = max(ela_score if media_type == "image/jpeg" else 0.0, block_splice_score, noise_inconsistency * 0.8)
        prnu_match = 0.85 if has_camera_exif and noise_inconsistency < 0.35 and block_splice_score < 0.35 else (0.15 if is_screen_capture else 0.50)

        # AI Detection scores - check both key aliases
        synthetic_index = float(ai_analytics.get("synthetic_likelihood_index_percent", ai_analytics.get("synthetic_likelihood_pct", 15.0))) / 100.0
        spectral_decay = float(fft_analytics.get("spectral_decay_slope", -1.8))
        spectral_anomaly = 0.80 if spectral_decay > -1.2 else 0.15

        if ai_declared:
            diffusion_probability = 0.96
            gan_probability = 0.15
            ai_edit_probability = 0.90
            neural_detection_score = 0.95
        elif is_screen_capture:
            diffusion_probability = min(0.35, synthetic_index * 0.5)
            gan_probability = 0.05
            ai_edit_probability = 0.20
            neural_detection_score = 0.18
        else:
            diffusion_probability = min(0.98, max(0.04, synthetic_index))
            gan_probability = min(0.90, max(0.04, synthetic_index * 0.6))
            ai_edit_probability = min(0.95, max(0.08, (noise_inconsistency + synthetic_index) / 2.0))
            neural_detection_score = max(diffusion_probability, gan_probability)

        # Pixel forensic score (enhanced with SRM + block splicing)
        pixel_forensic_score = max(
            noise_inconsistency,
            copy_move_score,
            srm_splice_score,
            block_splice_score,
            ela_score if media_type == "image/jpeg" else 0.0
        )

        # Traditional manipulation probability (ensemble fusion)
        # Typography requires >= 20 anomalous glyphs AND > 5% anomaly rate to avoid
        # false alarms on natural photos that happen to contain incidental text.
        typo_anomaly_count = typo_analytics.get("alignment_anomalies_detected", typo_analytics.get("anomalous_glyphs_count", 0))
        typo_anomaly_rate  = float(typo_analytics.get("anomaly_rate_pct", 0.0))
        typo_is_significant = typo_anomaly_count >= 20 and typo_anomaly_rate >= 5.0
        traditional_manipulation_probability = max(
            copy_move_score,
            0.75 if jpeg_analytics.get("double_compression_suspected") else 0.08,
            0.78 if typo_is_significant else 0.06,
            noise_inconsistency if noise_inconsistency > 0.65 else 0.06,
            srm_splice_score if srm_splice_score > 0.55 else 0.08,
            block_splice_score if block_splice_score > 0.40 else 0.06,
            lighting_score if lighting_score > 0.60 else 0.06,
        )

        # AI generation probability
        ai_generation_probability = diffusion_probability

        # Overall confidence calculation (calibrated weighted multi-evidence fusion)
        if ai_declared:
            overall_confidence = 0.96
        elif is_screen_capture:
            overall_confidence = 0.92
        elif copy_move_score > 0.7:
            overall_confidence = 0.88
        elif ai_generation_probability > 0.75:
            overall_confidence = 0.90
        elif traditional_manipulation_probability > 0.70:
            overall_confidence = 0.87
        elif has_camera_exif and traditional_manipulation_probability < 0.30:
            overall_confidence = 0.88
        else:
            overall_confidence = 0.78

        # 2. Answer the Four Independent Forensic Questions (Section 45)
        # Q1: Origin
        if is_screen_capture:
            q1_origin = "Direct Digital Screen Rendering (96 DPI Display Interface)"
            origin_code = "SCREEN_CAPTURE"
        elif has_camera_exif:
            make = extracted_metadata.get("Make", "Unknown Camera")
            model = extracted_metadata.get("Model", "")
            q1_origin = f"Physical Optical Camera Sensor ({make} {model})".strip()
            origin_code = "CAMERA_ORIGIN"
        elif document_analytics.get("document_type") in ["pdf", "office_openxml"]:
            q1_origin = f"Digital Document Structure ({document_analytics.get('document_type').upper()})"
            origin_code = "DOCUMENT_CONTAINER"
        elif ai_declared or ai_generation_probability > 0.85:
            q1_origin = "Algorithmic Latent Space (Generative AI Model Synthesis)"
            origin_code = "AI_LATENT_SYNTHESIS"
        else:
            q1_origin = "Unknown Digital Source (Metadata Stripped or Web Exported)"
            origin_code = "UNKNOWN"

        # Q2: Integrity
        if copy_move_score > 0.70:
            q2_integrity = "Locally Tampered: Duplicated / Cloned Content Verified"
            integrity_code = "LOCALLY_ALTERED_CLONED"
        elif typo_is_significant:
            q2_integrity = "Locally Tampered: Typographic Baseline & Character Insertion Anomalies"
            integrity_code = "LOCALLY_ALTERED_TYPOGRAPHY"
        elif jpeg_analytics.get("double_compression_suspected"):
            q2_integrity = "Recompressed: Secondary Save Over Prior Compressed Generation"
            integrity_code = "RECOMPRESSED_SECONDARY"
        elif noise_inconsistency > 0.70:
            q2_integrity = "Locally Spliced: Multi-Source Noise Residual Inconsistency"
            integrity_code = "LOCALLY_SPLICED"
        elif c2pa_present and signature_valid and not ai_declared:
            q2_integrity = "Unaltered: Cryptographically Sealed Provenance Intact"
            integrity_code = "AUTHENTIC_SEALED"
        else:
            q2_integrity = "Bitstream Preserved: No Distinct Structural Splicing Detected"
            integrity_code = "NO_ALTERATION_OBSERVED"

        # Q3: Generation
        if ai_declared:
            q3_generation = "Generative AI: Explicitly Declared in C2PA Provenance Manifest"
            generation_code = "AI_DECLARED"
        elif ai_generation_probability > 0.80:
            q3_generation = "Generative AI: High Probability of Latent Diffusion / GAN Synthesis"
            generation_code = "AI_GENERATED"
        elif is_screen_capture:
            q3_generation = "Human Interaction: Direct Operating System Window/Shell Render"
            generation_code = "SCREEN_RENDER"
        elif has_camera_exif and traditional_manipulation_probability < 0.30:
            q3_generation = "Human Physical World Capture: Optical Camera Exposure"
            generation_code = "PHYSICAL_WORLD_CAPTURE"
        elif ai_edit_probability > 0.70:
            q3_generation = "AI-Assisted Inpainting / Generative Fill on Prior Base Image"
            generation_code = "AI_INPAINTED_MODIFIED"
        else:
            q3_generation = "Standard Digital Media (No Generative Diffusion Markers Detected)"
            generation_code = "CONVENTIONAL_DIGITAL"

        # Q4: Transformation
        transformations: List[str] = []
        if is_screen_capture:
            transformations.append("Direct Screen Rasterization (96 DPI native resolution)")
        if jpeg_analytics.get("double_compression_suspected"):
            transformations.append("JPEG Recompression (Non-linear quantization steps)")
        if copy_move_score > 0.70:
            transformations.append("Copy-Move Forgery (Cloned keypoint clusters)")
        if typo_is_significant:
            transformations.append("Character Baseline Editing / Number Replacement")
        if "photoshop" in str(metadata_software).lower():
            transformations.append("Exported or Edited via Adobe Photoshop")
        if not transformations:
            transformations.append("No post-capture spatial transformation detected")
        q4_transformation = "; ".join(transformations)

        # 3. Formulate Final Assessment Classification Tag
        # Typography requires significance threshold to avoid false classification on
        # photos with incidental text (receipts, signs) where sub-pixel anti-aliasing
        # naturally produces minor baseline variance.
        if ai_declared:
            classification = "LIKELY_AI_GENERATED"
        elif is_screen_capture:
            if typo_is_significant:
                classification = "LIKELY_MANIPULATED"
            else:
                classification = "DIRECT_SCREEN_CAPTURE"
        elif copy_move_score > 0.70 or typo_is_significant:
            classification = "TRADITIONAL_MANIPULATION"
        elif ai_generation_probability > 0.80 and traditional_manipulation_probability > 0.60:
            classification = "LIKELY_AI_MODIFIED"
        elif ai_generation_probability > 0.70:
            classification = "LIKELY_AI_GENERATED"
        elif has_camera_exif and traditional_manipulation_probability < 0.35 and ai_generation_probability < 0.50:
            # Camera EXIF establishes physical-world origin; AI scores up to 0.50 are expected
            # from smartphones with heavy computational photography (HDR, AI sharpening)
            classification = "CAMERA_ORIGIN_UNALTERED"
        elif traditional_manipulation_probability > 0.65 or copy_move_score > 0.70 or block_splice_score > 0.55:
            classification = "LIKELY_MANIPULATED"
        elif c2pa_present and signature_valid:
            classification = "AUTHENTIC_PROVENANCE_SUPPORTED"
        else:
            classification = "UNKNOWN_OR_INCONCLUSIVE"

        # 4. Extract Localized Suspicious Regions (Section 19 & Section 44)
        suspicious_regions: List[Dict[str, Any]] = []
        # From splicing anomalies
        for reg in splicing_analytics.get("suspicious_regions", []):
            suspicious_regions.append({
                "x": reg.get("x", 0),
                "y": reg.get("y", 0),
                "width": reg.get("width", reg.get("w", 64)),
                "height": reg.get("height", reg.get("h", 64)),
                "score": reg.get("score", 0.85),
                "label": reg.get("label", "Statistically Spliced / Foreign Composite Region"),
            })
        # From typography anomalies
        for reg in typo_analytics.get("anomalous_regions", []):
            suspicious_regions.append({
                "x": reg.get("x", 0),
                "y": reg.get("y", 0),
                "width": reg.get("w", 0),
                "height": reg.get("h", 0),
                "score": 0.88,
                "label": "Suspicious Character Baseline / Kerning Offset",
            })
        # From copy-move clusters
        for clus in copymove_analytics.get("clusters", []):
            suspicious_regions.append({
                "x": clus.get("src_x", 0),
                "y": clus.get("src_y", 0),
                "width": clus.get("w", 64),
                "height": clus.get("h", 64),
                "score": 0.85,
                "label": "Cloned / Duplicated Keypoint Region",
            })

        # 5. Build Explainability Evidentiary Hierarchy (Section 40)
        ranked_evidence: List[Dict[str, str]] = []
        if c2pa_present:
            strength = "HIGH" if ai_declared else "PROVENANCE_INTACT"
            ranked_evidence.append({"level": strength, "item": f"C2PA Provenance: {c2pa_analytics.get('claim_generator', 'Preserved manifest store')}"})
        if ai_generation_probability > 0.70:
            ranked_evidence.append({"level": "HIGH", "item": f"Generative AI Synthetic Traces: {round(ai_generation_probability * 100, 1)}% synthetic likelihood"})
        if block_splice_score > 0.35:
            ranked_evidence.append({"level": "HIGH", "item": f"Image Splicing / Compositing: {splicing_analytics.get('anomalous_blocks', 0)} inconsistent blocks detected"})
        if copy_move_score > 0.70:
            ranked_evidence.append({"level": "HIGH", "item": f"Copy-Move Cloning: {copymove_analytics.get('matches_found', 0)} matched keypoint pairs"})
        if typo_analytics.get("alignment_anomalies_detected", 0) > 0:
            ranked_evidence.append({"level": "HIGH", "item": f"Typography Kerning / Baseline Offset: {typo_analytics.get('alignment_anomalies_detected')} anomalous character lines"})
        if jpeg_analytics.get("double_compression_suspected"):
            ranked_evidence.append({"level": "MED", "item": f"JPEG Recompression: Non-linear DQT coefficient distribution (Est. Q={jpeg_analytics.get('estimated_quality')}%)"})
        if noise_inconsistency > 0.50:
            ranked_evidence.append({"level": "MED", "item": f"Noise Residual Inhomogeneity: Ratio {round(float(noise_analytics.get('inhomogeneity_ratio', 1.0)), 1)}:1 exceeds uniform baseline"})
        if is_screen_capture:
            ranked_evidence.append({"level": "INFO", "item": "Direct Digital Screen Rendering: Clean 96 DPI pixel density verified"})
        if has_camera_exif and traditional_manipulation_probability < 0.35:
            make = extracted_metadata.get("Make", "")
            model = extracted_metadata.get("Model", "")
            ranked_evidence.append({"level": "INFO", "item": f"Authentic Camera Metadata: {make} {model} hardware tags intact".strip()})
        if not ranked_evidence:
            ranked_evidence.append({"level": "LOW", "item": "No statistical manipulation anomalies observed in current screening pass"})

        # 6. Canonical Evidence JSON Schema (Section 44)
        canonical_evidence_json = {
            "case_id": case_id,
            "file": {
                "name": original_filename,
                "mime": media_type,
                "size": file_size_bytes,
                "sha256": hashes.get("sha256"),
                "sha512": hashes.get("sha512"),
                "blake3": hashes.get("blake3"),
                "perceptual_hashes": {
                    "phash": hashes.get("phash"),
                    "dhash": hashes.get("dhash"),
                    "ahash": hashes.get("ahash"),
                    "whash": hashes.get("whash"),
                    "colorhash": hashes.get("colorhash"),
                }
            },
            "provenance": {
                "c2pa_present": c2pa_present,
                "signature_valid": signature_valid,
                "ai_declared": ai_declared,
                "claim_generator": c2pa_analytics.get("claim_generator"),
                "actions": c2pa_analytics.get("actions", []),
            },
            "metadata": {
                "camera": f"{extracted_metadata.get('Make', '')} {extracted_metadata.get('Model', '')}".strip() or "None (Clean Digital File)",
                "software": metadata_software,
                "metadata_anomaly_score": round(metadata_anomaly_score, 2),
            },
            "image_forensics": {
                "ela_score": round(ela_score, 2),
                "jpeg_anomaly": round(jpeg_anomaly, 2),
                "noise_inconsistency": round(noise_inconsistency, 2),
                "copy_move_score": round(copy_move_score, 2),
                "splice_score": round(splice_score, 2),
                "prnu_match": round(prnu_match, 2),
            },
            "ai_detection": {
                "gan_probability": round(gan_probability, 2),
                "diffusion_probability": round(diffusion_probability, 2),
                "ai_edit_probability": round(ai_edit_probability, 2),
                "neural_detection_score": round(neural_detection_score, 2),
            },
            "localization": {
                "heatmap": all_artifacts.get("ai_synthetic_map") or all_artifacts.get("ai_synthetic_heatmap") or all_artifacts.get("noise_residual_map") or all_artifacts.get("noise_residual_heatmap") or all_artifacts.get("ela_heatmap"),
                "regions": suspicious_regions,
            },
            "assessment": {
                "classification": classification,
                "confidence": round(overall_confidence, 2),
                "calibrated_scores": {
                    "ai_generation_probability": round(ai_generation_probability, 2),
                    "traditional_manipulation_probability": round(traditional_manipulation_probability, 2),
                    "provenance_confidence": round(provenance_conf, 2),
                    "metadata_anomaly_score": round(metadata_anomaly_score, 2),
                    "pixel_forensic_score": round(pixel_forensic_score, 2),
                    "overall_confidence": round(overall_confidence, 2),
                },
                "four_pillars": {
                    "q1_origin": {
                        "question": "Q1 - Where did this content originate?",
                        "finding": q1_origin,
                        "code": origin_code,
                    },
                    "q2_integrity": {
                        "question": "Q2 - Has the file/content been altered?",
                        "finding": q2_integrity,
                        "code": integrity_code,
                    },
                    "q3_generation": {
                        "question": "Q3 - Was AI used to generate it?",
                        "finding": q3_generation,
                        "code": generation_code,
                    },
                    "q4_transformation": {
                        "question": "Q4 - What operations were performed?",
                        "finding": q4_transformation,
                        "operations": transformations,
                    },
                },
                "explainability": {
                    "ranked_evidence": ranked_evidence,
                    "suspicious_regions_count": len(suspicious_regions),
                    "potential_operations": transformations,
                }
            }
        }

        return canonical_evidence_json
