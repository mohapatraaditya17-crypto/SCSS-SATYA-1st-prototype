from fastapi import APIRouter
from app.core.config import settings

router = APIRouter()


@router.get("/health", tags=["System"])
def get_health():
    """
    Returns application health status, active algorithm manifest,
    and storage directories status.
    """
    vault_accessible = settings.VAULT_DIR.exists()
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "pipeline_version": settings.PIPELINE_VERSION,
        "vault_accessible": vault_accessible,
        "core_principle": settings.CORE_PRINCIPLE,
    }


@router.get("/version", tags=["System"])
def get_version():
    """
    Returns platform manifest, method versions, and standard compliance frameworks.
    """
    return {
        "platform": settings.PROJECT_FULL_NAME,
        "version": settings.VERSION,
        "analysis_pipeline_version": settings.PIPELINE_VERSION,
        "methods": settings.METHOD_VERSIONS,
        "disclaimer": settings.MANDATORY_DISCLAIMER,
        "organization": settings.ORGANIZATION,
    }
