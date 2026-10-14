import os
from pathlib import Path
from typing import Dict, Any, List, Tuple
from datetime import datetime, timezone

from app.core.config import settings
from app.schemas.examination import ScreeningTestResult
from app.analysis.metadata_analyzer import MetadataAnalyzer
from app.analysis.integrity_analyzer import IntegrityAnalyzer
from app.analysis.ela_analyzer import ELAAnalyzer
from app.analysis.consistency_analyzer import ConsistencyAnalyzer


class ForensicPipeline:
    PIPELINE_VERSION = settings.PIPELINE_VERSION

    STANDARD_SUGGESTED_MANUAL_CHECKS: List[str] = [
        "Inspect original hardware or source storage device directly where possible (camera SD card, mobile device bitstream acquisition).",
        "Perform optical shadow and lighting direction consistency analysis across objects and subjects.",
        "Compare suspected facial or edge boundaries at 400%+ magnification for pixel interpolation or blending feather artifacts.",
        "Query reference reverse-image search databases (TinEye, Google Lens) to determine prior online publications or unedited source candidates.",
        "Verify camera hardware serial numbers against manufacturer registration or other known specimens from the same device.",
        "Examine discrete cosine transform (DCT) coefficient histograms with specialized tools (JPEGsnoop) if double-compression is suspected.",
    ]

    STANDARD_KNOWN_LIMITATIONS: List[str] = [
        "Preliminary screening tool: Automated indicators do not constitute legal proof or definitive forensic determination.",
        "Social media platforms, messaging apps, and content management systems routinely strip EXIF metadata and recompress imagery.",
        "High-quality recompression or intentional blur filtering can suppress or mask Error Level Analysis differences.",
        "Absence of detected manipulation indicators does not establish that an image is authentic or unaltered.",
        "Passive-blind screening methods do not guarantee detection of sophisticated deep generative AI models (GANs/diffusion) without watermarks.",
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
        Executes the 4-layer defensible screening pipeline.
        Returns all test results, artifacts, extracted metadata, and synthesized workflow assessment.
        """
        all_tests: List[ScreeningTestResult] = []
        all_artifacts: Dict[str, str] = {}

        # 1. Test A: File and metadata examination
        meta_res = MetadataAnalyzer.analyze(file_bytes, image_width, image_height, media_type)
        all_tests.append(meta_res["test_result"])
        extracted_metadata = meta_res["extracted_metadata"]

        # Parse capture timestamp from EXIF if available
        capture_timestamp = None
        raw_date = extracted_metadata.get("DateTimeOriginal") or extracted_metadata.get("DateTime")
        if raw_date:
            try:
                # Format: "YYYY:MM:DD HH:MM:SS"
                date_str = str(raw_date).strip().replace("/", ":")
                dt = datetime.strptime(date_str[:19], "%Y:%m:%d %H:%M:%S")
                capture_timestamp = dt.replace(tzinfo=timezone.utc)
            except Exception:
                pass

        # 2. Test B: SHA-256 evidence integrity
        integrity_test = IntegrityAnalyzer.analyze(sha256_digest, file_size_bytes)
        all_tests.append(integrity_test)

        # 3. Test C: Error Level Analysis (ELA)
        ela_test, ela_artifacts = ELAAnalyzer.analyze(image_path, examination_id, media_type)
        all_tests.append(ela_test)
        all_artifacts.update(ela_artifacts)

        # 4. Test D: Basic image consistency checks
        consistency_test, consistency_artifacts, consistency_analytics = ConsistencyAnalyzer.analyze(
            image_path, examination_id, media_type, extracted_metadata
        )
        all_tests.append(consistency_test)
        all_artifacts.update(consistency_artifacts)
        if "channels" in consistency_analytics:
            all_artifacts["channel_analytics"] = consistency_analytics["channels"]

        # Synthesize overall preliminary workflow assessment
        indicators_count = sum(1 for t in all_tests if t.indicator == "indicator_detected")
        inconclusive_count = sum(1 for t in all_tests if t.indicator == "inconclusive")

        if indicators_count > 0:
            overall_assessment = "requires_human_review"
        elif inconclusive_count > 0:
            overall_assessment = "requires_human_review"
        else:
            overall_assessment = "no_indicators_detected"

        return {
            "tests": all_tests,
            "artifacts": all_artifacts,
            "extracted_metadata": extracted_metadata,
            "capture_timestamp": capture_timestamp,
            "overall_assessment": overall_assessment,
            "known_limitations": cls.STANDARD_KNOWN_LIMITATIONS,
            "suggested_manual_checks": cls.STANDARD_SUGGESTED_MANUAL_CHECKS,
        }
