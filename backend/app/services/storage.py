import io
import os
import uuid
import hashlib
from pathlib import Path
from typing import Tuple, Dict, Any, Optional
from PIL import Image

from app.core.config import settings

# Enforce decompression bomb protection
Image.MAX_IMAGE_PIXELS = settings.MAX_IMAGE_PIXELS


class StorageService:
    @staticmethod
    def validate_file_signature(file_bytes: bytes) -> str:
        """
        Validates magic bytes to determine true file type.
        Does not trust user-provided MIME type or extension.
        """
        if len(file_bytes) < 12:
            raise ValueError("File is too small to be a valid image.")

        if file_bytes.startswith(b"\xFF\xD8\xFF"):
            return "image/jpeg"
        elif file_bytes.startswith(b"\x89PNG\r\n\x1a\n"):
            return "image/png"
        elif file_bytes.startswith(b"RIFF") and file_bytes[8:12] == b"WEBP":
            return "image/webp"
        else:
            raise ValueError("Unsupported or invalid file format. Supported formats: JPEG, PNG, WebP.")

    @staticmethod
    def compute_hashes(file_bytes: bytes) -> Dict[str, str]:
        """
        Calculates SHA-256, SHA-1, and MD5 hashes directly from original bytes.
        SHA-256 serves as the primary cryptographic integrity reference.
        """
        sha256 = hashlib.sha256(file_bytes).hexdigest()
        sha1 = hashlib.sha1(file_bytes).hexdigest()
        md5 = hashlib.md5(file_bytes).hexdigest()
        return {
            "sha256": sha256,
            "sha1": sha1,
            "md5": md5,
        }

    @classmethod
    def ingest_evidence(
        cls, file_bytes: bytes, original_filename: str
    ) -> Tuple[Dict[str, Any], Path]:
        """
        Validates, decodes safely, computes cryptographic seals,
        and saves raw bytes non-invasively to the evidence vault.
        """
        # 1. Enforce size limit
        file_size = len(file_bytes)
        if file_size > settings.MAX_UPLOAD_SIZE_BYTES:
            max_mb = settings.MAX_UPLOAD_SIZE_BYTES / (1024 * 1024)
            raise ValueError(f"File size exceeds maximum permitted limit of {max_mb:.0f} MB.")

        if file_size == 0:
            raise ValueError("Uploaded file contains zero bytes.")

        # 2. Magic byte file signature validation
        detected_mime = cls.validate_file_signature(file_bytes)

        # 3. Safe PIL decoding check & dimension validation
        try:
            with Image.open(io.BytesIO(file_bytes)) as img:
                img.verify()  # Verifies structural integrity without fully decoding
        except Exception as e:
            raise ValueError(f"Corrupted or invalid image stream: {str(e)}")

        # Re-open for dimension and mode extraction
        try:
            with Image.open(io.BytesIO(file_bytes)) as img:
                width, height = img.size
                color_mode = img.mode
                if width <= 0 or height <= 0:
                    raise ValueError("Invalid image dimensions detected.")
        except Exception as e:
            raise ValueError(f"Failed to inspect image dimensions: {str(e)}")

        # 4. Calculate cryptographic digests
        hashes = cls.compute_hashes(file_bytes)

        # 5. Sanitize filename and create secure vault filename
        ext = ".jpg" if detected_mime == "image/jpeg" else (".png" if detected_mime == "image/png" else ".webp")
        clean_original_filename = Path(original_filename).name  # Prevent directory traversal
        safe_stored_filename = f"{uuid.uuid4().hex}_{hashes['sha256'][:10]}{ext}"

        vault_path = settings.VAULT_DIR / safe_stored_filename
        if vault_path.exists():
            raise ValueError("Collision detected: evidence record already exists in vault.")

        # 6. Save original raw bytes preserving bitstream
        with open(vault_path, "wb") as f:
            f.write(file_bytes)

        metadata = {
            "original_filename": clean_original_filename,
            "stored_filename": safe_stored_filename,
            "file_size_bytes": file_size,
            "detected_media_type": detected_mime,
            "image_width": width,
            "image_height": height,
            "color_mode": color_mode,
            "sha256_digest": hashes["sha256"],
            "sha1_digest": hashes["sha1"],
            "md5_digest": hashes["md5"],
        }

        return metadata, vault_path

    @classmethod
    def recompute_vault_hash(cls, stored_filename: str) -> Optional[str]:
        """
        Reads original stored bytes from vault and recomputes SHA-256 for integrity verification.
        """
        safe_filename = Path(stored_filename).name  # Prevent path traversal
        file_path = settings.VAULT_DIR / safe_filename
        if not file_path.exists():
            return None

        with open(file_path, "rb") as f:
            data = f.read()
        return hashlib.sha256(data).hexdigest()
