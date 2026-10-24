import os
from pathlib import Path
from typing import Dict, Any, List, Tuple
from datetime import datetime, timezone

from app.core.config import settings
from app.schemas.examination import ScreeningTestResult
from app.analysis.metadata_analyzer import MetadataAnalyzer
from app.analysis.integrity_analyzer import IntegrityAnalyzer
from app.analysis.hash_analyzer import HashAnalyzer
from app.analysis.c2pa_analyzer import C2PAAnalyzer
from app.analysis.document_forensics_analyzer import DocumentForensicsAnalyzer
from app.analysis.jpeg_quantization_analyzer import JPEGQuantizationAnalyzer
from app.analysis.ela_analyzer import ELAAnalyzer
from app.analysis.consistency_analyzer import ConsistencyAnalyzer
from app.analysis.noise_analyzer import NoiseAnalyzer
from app.analysis.fft_analyzer import FFTAnalyzer
from app.analysis.copymove_analyzer import CopyMoveAnalyzer
from app.analysis.ai_synthetic_analyzer import AISyntheticAnalyzer
from app.analysis.typography_analyzer import TypographyAnalyzer
from app.analysis.srm_wavelet_analyzer import SRMWaveletAnalyzer
from app.analysis.splicing_detector import SplicingDetector
from app.analysis.lighting_consistency_analyzer import LightingConsistencyAnalyzer
from app.analysis.evidence_fusion import EvidenceFusionEngine


class ForensicPipeline:
    PIPELINE_VERSION = "2026.4"

    STANDARD_SUGGESTED_MANUAL_CHECKS: List[str] = [
        "Inspect original hardware or source storage device directly where possible (camera SD card, mobile device bitstream acquisition).",
        "Perform optical shadow and lighting direction consistency analysis across objects and subjects.",
        "Compare suspected facial, boundary, or text edges at 400%+ magnification for pixel interpolation or feathering artifacts.",
        "Query reference reverse-image search databases (TinEye, Google Lens) to determine prior online publications or unedited source candidates.",
        "Verify camera hardware serial numbers against manufacturer registration or other known specimens from the same device.",
        "Examine discrete cosine transform (DCT) coefficient histograms with specialized tools (JPEGsnoop) if double-compression is suspected.",
        "Verify font metrics, kerning, and pixel alignment under high contrast for digital documents and interface screenshots.",
        "Assess localized high-frequency diffusion residuals to verify AI synthesis indications.",
        "Inspect C2PA manifest certificate chains against the Adobe / C2PA Trust List where available.",
    ]

    STANDARD_KNOWN_LIMITATIONS: List[str] = [
        "Preliminary screening tool: Automated indicators do not constitute legal proof or definitive forensic determination.",
        "Social media platforms, messaging apps, and content management systems routinely strip EXIF metadata and recompress imagery.",
        "High-quality recompression or intentional blur filtering can suppress or mask Error Level Analysis differences.",
        "Absence of detected manipulation indicators does not establish that an image is authentic or unaltered.",
        "Passive-blind screening methods evaluate statistical anomalies; sophisticated diffusion models (DALL-E 3, Midjourney v6) evolve rapidly.",
        "Screenshots and flat UI graphics naturally lack optical sensor noise and camera EXIF records.",
        "C2PA provenance manifests require unbroken cryptographic chains; file format conversions drop external manifest bindings.",
    ]

    @classmethod
    def execute(
        cls,
        image_path: Path,
        file_bytes: bytes,
        examination_id: str,
        media_type: str,
        image_width: int,
        image_height: int,
        sha256_digest: str,
        file_size_bytes: int,
    ) -> Dict[str, Any]:
        """
        Executes the comprehensive multi-layer digital media forensics pipeline.
        Produces full screening test results, visual artifacts, analytics, and canonical evidence JSON.
        """
        all_tests: List[ScreeningTestResult] = []
        all_artifacts: Dict[str, Any] = {}

        # 1. Test 1: Metadata & Deep Structural Chunk Forensics
        meta_res = MetadataAnalyzer.analyze(file_bytes, image_width, image_height, media_type)
        all_tests.append(meta_res["test_result"])
        extracted_metadata = meta_res["extracted_metadata"]

        # Parse capture timestamp
        capture_timestamp = None
        raw_date = (
            extracted_metadata.get("DateTimeOriginal") or
            extracted_metadata.get("DateTime") or
            extracted_metadata.get("PNG:LastModified")
        )
        if raw_date:
            try:
                date_str = str(raw_date).strip().replace("/", ":")
                dt = datetime.strptime(date_str[:19], "%Y:%m:%d %H:%M:%S")
                capture_timestamp = dt.replace(tzinfo=timezone.utc)
            except Exception:
                pass

        # 2. Test 2: Dual Cryptographic & Perceptual Hashing (SHA-256, BLAKE3, pHash, dHash, etc.)
        hash_test, _, hash_analytics = HashAnalyzer.analyze(image_path, file_bytes, file_size_bytes)
        all_tests.append(hash_test)
        if hash_analytics:
            all_artifacts["hash_analytics"] = hash_analytics

        # 3. Test 3: C2PA & Content Credentials Cryptographic Provenance
        c2pa_test, c2pa_analytics = C2PAAnalyzer.analyze(file_bytes, media_type, extracted_metadata)
        all_tests.append(c2pa_test)
        all_artifacts["c2pa_analytics"] = c2pa_analytics

        # 4. Test 4: Document & Container Structural Forensics
        doc_test, doc_analytics = DocumentForensicsAnalyzer.analyze(file_bytes, image_path, media_type)
        all_tests.append(doc_test)
        all_artifacts["document_analytics"] = doc_analytics

        # 5. Test 5: JPEG Quantization (DQT) & Double-Compression Analysis
        jpeg_test, jpeg_analytics = JPEGQuantizationAnalyzer.analyze(file_bytes, media_type)
        all_tests.append(jpeg_test)
        all_artifacts["jpeg_analytics"] = jpeg_analytics

        # 6. Test 6: Error Level Analysis (ELA - JPEG DCT Compression Grids)
        ela_test, ela_artifacts = ELAAnalyzer.analyze(image_path, examination_id, media_type)
        all_tests.append(ela_test)
        all_artifacts.update(ela_artifacts)

        # 7. Test 7: Image Consistency & Channel Analytics
        consistency_test, consistency_artifacts, consistency_analytics = ConsistencyAnalyzer.analyze(
            image_path, examination_id, media_type, extracted_metadata
        )
        all_tests.append(consistency_test)
        all_artifacts.update(consistency_artifacts)
        if "channels" in consistency_analytics:
            all_artifacts["channel_analytics"] = consistency_analytics["channels"]
        if "quadrant_variance" in consistency_analytics:
            all_artifacts["quadrant_variance"] = consistency_analytics["quadrant_variance"]

        # 8. Test 8: Multi-Scale Noise Inconsistency & Residual Analysis
        noise_test, noise_artifacts, noise_analytics = NoiseAnalyzer.analyze(
            image_path, examination_id, media_type
        )
        all_tests.append(noise_test)
        all_artifacts.update(noise_artifacts)
        if noise_analytics:
            all_artifacts["noise_analytics"] = noise_analytics

        # 9. Test 9: 2D Fourier Spectral Analysis (FFT Frequency & Lattice Artifacts)
        fft_test, fft_artifacts, fft_analytics = FFTAnalyzer.analyze(
            image_path, examination_id, media_type
        )
        all_tests.append(fft_test)
        all_artifacts.update(fft_artifacts)
        if fft_analytics:
            all_artifacts["fft_analytics"] = fft_analytics

        # 10. Test 10: Copy-Move / Clone Forgery Detection (Keypoint Descriptor Matching)
        copymove_test, copymove_artifacts, copymove_analytics = CopyMoveAnalyzer.analyze(
            image_path, examination_id, media_type
        )
        all_tests.append(copymove_test)
        all_artifacts.update(copymove_artifacts)
        if copymove_analytics:
            all_artifacts["copymove_analytics"] = copymove_analytics

        # 11. Test 11: AI Generative Classifier (Spectral Decay Slope & Synthetic Traces)
        ai_test, ai_artifacts, ai_analytics = AISyntheticAnalyzer.analyze(
            image_path, examination_id, media_type
        )
        all_tests.append(ai_test)
        all_artifacts.update(ai_artifacts)
        if ai_analytics:
            all_artifacts["ai_synthetic_analytics"] = ai_analytics

        # 12. Test 12: Document Typography & Character Alignment Engine (Glyph & Kerning Variance)
        typo_test, typo_artifacts, typo_analytics = TypographyAnalyzer.analyze(
            image_path, examination_id, media_type
        )
        all_tests.append(typo_test)
        all_artifacts.update(typo_artifacts)
        if typo_analytics:
            all_artifacts["typography_analytics"] = typo_analytics

        # 13. Test 13: SRM Spatial Rich Model & Wavelet Residual Analysis
        srm_test, _, srm_analytics = SRMWaveletAnalyzer.analyze(
            image_path, examination_id, media_type
        )
        all_tests.append(srm_test)
        if srm_analytics:
            all_artifacts["srm_analytics"] = srm_analytics

        # 14. Test 14: Splicing & Composite Forgery Detection
        splice_test, _, splice_analytics = SplicingDetector.analyze(
            image_path, examination_id, media_type
        )
        all_tests.append(splice_test)
        if splice_analytics:
            all_artifacts["splicing_analytics"] = splice_analytics

        # 15. Test 15: Illumination Direction & Geometric Consistency
        lighting_test, _, lighting_analytics = LightingConsistencyAnalyzer.analyze(
            image_path, examination_id, media_type
        )
        all_tests.append(lighting_test)
        if lighting_analytics:
            all_artifacts["lighting_analytics"] = lighting_analytics

        # 16. Multi-Layer Evidence Fusion & Correlation Engine
        # Gather hashes dictionary
        hashes = {
            "sha256": sha256_digest,
            "sha512": hash_analytics.get("cryptographic", {}).get("sha512"),
            "blake3": hash_analytics.get("cryptographic", {}).get("blake3"),
            "phash": hash_analytics.get("perceptual", {}).get("phash"),
            "dhash": hash_analytics.get("perceptual", {}).get("dhash"),
            "ahash": hash_analytics.get("perceptual", {}).get("ahash"),
            "whash": hash_analytics.get("perceptual", {}).get("whash"),
            "colorhash": hash_analytics.get("perceptual", {}).get("colorhash"),
        }

        canonical_evidence = EvidenceFusionEngine.fuse_evidence(
            case_id=examination_id,
            original_filename=image_path.name,
            media_type=media_type,
            file_size_bytes=file_size_bytes,
            hashes=hashes,
            extracted_metadata=extracted_metadata,
            c2pa_analytics=c2pa_analytics,
            jpeg_analytics=jpeg_analytics,
            document_analytics=doc_analytics,
            all_artifacts=all_artifacts,
            all_tests=all_tests,
        )

        all_artifacts["canonical_evidence"] = canonical_evidence
        all_artifacts["assessment_summary"] = canonical_evidence["assessment"]

        # Determine preliminary workflow assessment
        classification = canonical_evidence["assessment"]["classification"]
        if classification in ["LIKELY_AI_MODIFIED", "LIKELY_AI_GENERATED", "TRADITIONAL_MANIPULATION", "LIKELY_MANIPULATED"]:
            overall_assessment = "requires_human_review"
        elif classification in ["AUTHENTIC_PROVENANCE_SUPPORTED", "CAMERA_ORIGIN_UNALTERED", "DIRECT_SCREEN_CAPTURE"]:
            # Check if any individual high test flagged an indicator
            indicators_count = sum(1 for t in all_tests if t.indicator == "indicator_detected" and "C2PA" not in t.method)
            overall_assessment = "requires_human_review" if indicators_count > 0 else "no_indicators_detected"
        else:
            overall_assessment = "requires_human_review"

        return {
            "tests": all_tests,
            "artifacts": all_artifacts,
            "extracted_metadata": extracted_metadata,
            "capture_timestamp": capture_timestamp,
            "overall_assessment": overall_assessment,
            "canonical_evidence": canonical_evidence,
            "known_limitations": cls.STANDARD_KNOWN_LIMITATIONS,
            "suggested_manual_checks": cls.STANDARD_SUGGESTED_MANUAL_CHECKS,
        }
