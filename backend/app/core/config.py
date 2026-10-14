import os
from pathlib import Path
from typing import List, Set
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(case_sensitive=True, extra="allow")

    PROJECT_NAME: str = "SCSS SATYA"
    PROJECT_FULL_NAME: str = "SCSS SATYA — Forensic Image Authenticity Screening Platform"
    TAGLINE: str = "Forensic-led digital image authenticity screening platform"
    VERSION: str = "1.0.0"
    PIPELINE_VERSION: str = "2026.1"
    ORGANIZATION: str = "Sure Clue Scientific Solutions (SCSS)"
    CORE_PRINCIPLE: str = "The tool screens. The expert decides."

    MANDATORY_DISCLAIMER: str = (
        "SCSS SATYA produces preliminary, automated image-screening findings for "
        "investigative support. Its results are not a definitive determination of "
        "authenticity, manipulation, source, intent, or legal admissibility. The absence "
        "of detected indicators does not establish that an image is authentic. "
        "Findings require interpretation by a qualified forensic examiner and must be "
        "considered alongside other available evidence."
    )

    # Base Paths
    BACKEND_DIR: Path = Path(__file__).resolve().parent.parent.parent
    ROOT_DIR: Path = BACKEND_DIR.parent
    STORAGE_DIR: Path = ROOT_DIR / "storage"
    VAULT_DIR: Path = STORAGE_DIR / "vault"
    ARTIFACTS_DIR: Path = STORAGE_DIR / "artifacts"
    REPORTS_DIR: Path = STORAGE_DIR / "reports"

    # Database
    DATABASE_URL: str = f"sqlite:///{STORAGE_DIR / 'satya_forensics.db'}"

    # File Upload Limits & Security
    MAX_UPLOAD_SIZE_BYTES: int = 15 * 1024 * 1024  # 15 MB
    MAX_IMAGE_PIXELS: int = 50_000_000  # 50 Megapixels max (decompression bomb protection)
    ALLOWED_EXTENSIONS: Set[str] = {".jpg", ".jpeg", ".png", ".webp"}
    ALLOWED_MIME_TYPES: Set[str] = {"image/jpeg", "image/png", "image/webp"}

    # Method Names and Versions
    METHOD_VERSIONS: dict = {
        "metadata_examination": "1.0.0",
        "sha256_integrity": "1.0.0",
        "error_level_analysis": "1.0.0",
        "image_consistency_checks": "1.0.0",
    }

    # CORS Allowed Origins
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ]


settings = Settings()

# Ensure storage directories exist
settings.VAULT_DIR.mkdir(parents=True, exist_ok=True)
settings.ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
settings.REPORTS_DIR.mkdir(parents=True, exist_ok=True)
