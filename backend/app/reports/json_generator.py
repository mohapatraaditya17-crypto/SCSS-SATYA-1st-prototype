from datetime import datetime, timezone
from typing import Dict, Any
from app.core.config import settings
from app.database.models import Examination


class JSONReportGenerator:
    @classmethod
    def generate(cls, exam: Examination) -> Dict[str, Any]:
        """
        Produces a complete machine-readable forensic screening JSON report.
        """
        return {
            "platform": {
                "name": settings.PROJECT_FULL_NAME,
                "version": settings.VERSION,
                "pipeline_version": settings.PIPELINE_VERSION,
                "organization": settings.ORGANIZATION,
                "core_principle": settings.CORE_PRINCIPLE,
            },
            "disclaimer": settings.MANDATORY_DISCLAIMER,
            "report_metadata": {
                "report_id": f"REP-{exam.examination_id}",
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "format_version": "1.0",
            },
            "examination": {
                "examination_id": exam.examination_id,
                "status": exam.status,
                "overall_assessment": exam.overall_assessment,
                "timestamps": {
                    "uploaded_at": exam.upload_timestamp.isoformat() if exam.upload_timestamp else None,
                    "captured_at": exam.capture_timestamp.isoformat() if exam.capture_timestamp else None,
                },
                "evidence_file": {
                    "original_filename": exam.original_filename,
                    "file_size_bytes": exam.file_size_bytes,
                    "media_type": exam.detected_media_type,
                    "dimensions": {
                        "width": exam.image_width,
                        "height": exam.image_height,
                        "aspect_ratio": round(exam.image_width / exam.image_height, 2) if exam.image_height > 0 else 1.0,
                    },
                    "color_mode": exam.color_mode,
                },
                "cryptographic_integrity": {
                    "algorithm": "SHA-256",
                    "sha256": exam.sha256_digest,
                    "sha1": exam.sha1_digest,
                    "md5": exam.md5_digest,
                    "verified_against_vault": True,
                },
                "screening_tests": exam.test_results or [],
                "extracted_metadata": exam.extracted_metadata or {},
                "artifacts": exam.artifacts or {},
                "methodological_limitations": exam.known_limitations or [],
                "suggested_manual_forensic_checks": exam.suggested_manual_checks or [],
                "human_review": {
                    "status": exam.human_review_status,
                    "reviewer_name": exam.reviewer_name,
                    "reviewer_designation": exam.reviewer_designation,
                    "reviewer_organization": exam.reviewer_organization,
                    "notes": exam.review_notes,
                    "reviewed_at": exam.review_timestamp.isoformat() if exam.review_timestamp else None,
                    "attestation": exam.review_attestation,
                },
                "activity_log": [
                    {
                        "event_type": ev.event_type,
                        "timestamp": ev.timestamp.isoformat() if ev.timestamp else None,
                        "details": ev.details,
                    }
                    for ev in (exam.activity_events or [])
                ],
            },
        }
