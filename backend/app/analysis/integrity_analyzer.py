import time
from typing import Dict, Any, List
from app.schemas.examination import ScreeningTestResult


class IntegrityAnalyzer:
    METHOD_NAME = "sha256_integrity"
    VERSION = "1.0.0"

    @classmethod
    def analyze(cls, sha256_digest: str, file_size_bytes: int) -> ScreeningTestResult:
        start_time = time.perf_counter()
        observations: List[str] = [
            f"Computed cryptographic SHA-256 digest: {sha256_digest}",
            f"Evidence bitstream size: {file_size_bytes} bytes ({file_size_bytes / 1024:.2f} KB).",
            "Bitstream archived non-invasively in secure evidence vault.",
        ]
        limitations: List[str] = [
            "A cryptographic hash only verifies that stored bytes have not changed since upload.",
            "A matching SHA-256 hash does NOT prove that the image is an authentic, unaltered real-world capture.",
            "A manipulated or synthetic image generates a valid SHA-256 digest just like any genuine image."
        ]

        explanation = (
            "Cryptographic hashing established an initial tamper-evident baseline for the submitted evidence. "
            "Any future byte alteration or bit rot will cause hash verification to fail. However, cryptographic "
            "hashes attest solely to post-upload bitstream preservation, not the historical authenticity or "
            "camera provenance of the image."
        )

        exec_time = round((time.perf_counter() - start_time) * 1000, 2)

        return ScreeningTestResult(
            method=cls.METHOD_NAME,
            version=cls.VERSION,
            status="completed",
            indicator="no_indicator_detected",
            indicator_label="No indicator detected by this test",
            observations=observations,
            explanation=explanation,
            limitations=limitations,
            execution_time_ms=exec_time,
        )
