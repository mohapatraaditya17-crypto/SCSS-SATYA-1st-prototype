import hashlib
import time
from pathlib import Path
from typing import Dict, Any, List, Tuple
from PIL import Image
import imagehash
import blake3

from app.schemas.examination import ScreeningTestResult


class HashAnalyzer:
    METHOD_NAME = "cryptographic_and_perceptual_hashing"
    VERSION = "2.0.0"

    @classmethod
    def analyze(
        cls,
        image_path: Path,
        file_bytes: bytes,
        file_size_bytes: int,
    ) -> Tuple[ScreeningTestResult, Dict[str, Any], Dict[str, Any]]:
        start_time = time.perf_counter()
        observations: List[str] = []
        analytics: Dict[str, Any] = {}
        limitations: List[str] = [
            "Cryptographic hashes (SHA-256, BLAKE3, SHA-512) detect bit-level byte modification; a 1-bit alteration completely changes the hash.",
            "Perceptual hashes (pHash, dHash, aHash, wHash) detect visual appearance similarity and survive compression, resizing, and minor color adjustments.",
            "A matching hash proves bitstream preservation or visual correspondence, but does not prove the historical authenticity of the depicted scene."
        ]

        # 1. Cryptographic Hashes
        sha256_hash = hashlib.sha256(file_bytes).hexdigest()
        sha512_hash = hashlib.sha512(file_bytes).hexdigest()
        blake3_hash = blake3.blake3(file_bytes).hexdigest()

        analytics["cryptographic"] = {
            "sha256": sha256_hash,
            "sha512": sha512_hash,
            "blake3": blake3_hash,
            "file_size_bytes": file_size_bytes,
        }

        # 2. Perceptual Hashes (Visual Fingerprints)
        perceptual_hashes: Dict[str, str] = {}
        try:
            with Image.open(image_path) as img:
                rgb_img = img.convert("RGB")
                phash_val = str(imagehash.phash(rgb_img))
                dhash_val = str(imagehash.dhash(rgb_img))
                ahash_val = str(imagehash.average_hash(rgb_img))
                whash_val = str(imagehash.whash(rgb_img))
                colorhash_val = str(imagehash.colorhash(rgb_img))

                perceptual_hashes = {
                    "phash": phash_val,
                    "dhash": dhash_val,
                    "ahash": ahash_val,
                    "whash": whash_val,
                    "colorhash": colorhash_val,
                }
        except Exception:
            perceptual_hashes = {
                "phash": "N/A",
                "dhash": "N/A",
                "ahash": "N/A",
                "whash": "N/A",
                "colorhash": "N/A",
            }

        analytics["perceptual"] = perceptual_hashes

        observations.append(f"SHA-256: {sha256_hash[:16]}...{sha256_hash[-8:]}")
        observations.append(f"BLAKE3: {blake3_hash[:16]}...{blake3_hash[-8:]}")
        observations.append(f"pHash (DCT frequency fingerprint): {perceptual_hashes.get('phash')}")
        observations.append(f"dHash (Gradient difference fingerprint): {perceptual_hashes.get('dhash')}")
        observations.append(f"wHash (Wavelet DWT fingerprint): {perceptual_hashes.get('whash')}")

        explanation = (
            "Cryptographic hashing established dual tamper-evident baselines (SHA-256 and BLAKE3). "
            "Perceptual hashing generated multi-resolution visual fingerprints (pHash, dHash, wHash) "
            "enabling reverse lookup of visually identical screenshots, crops, or transcoded variants."
        )

        exec_time = round((time.perf_counter() - start_time) * 1000, 2)
        test_result = ScreeningTestResult(
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

        return test_result, {}, analytics
