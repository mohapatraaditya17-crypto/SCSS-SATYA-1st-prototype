from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class FileIntegrityInfo(BaseModel):
    algorithm: str = "SHA-256"
    digest: str
    sha1: Optional[str] = None
    md5: Optional[str] = None
    verified: Optional[bool] = None


class ScreeningTestResult(BaseModel):
    method: str
    version: str
    status: str  # completed, not_applicable, failed
    indicator: str  # indicator_detected, no_indicator_detected, inconclusive, test_unavailable, test_failed
    indicator_label: str  # Human readable label
    observations: List[str] = Field(default_factory=list)
    explanation: str
    limitations: List[str] = Field(default_factory=list)
    execution_time_ms: float = 0.0


class ActivityEventResponse(BaseModel):
    id: int
    event_type: str
    timestamp: datetime
    details: Dict[str, Any] = Field(default_factory=dict)


class HumanReviewSubmission(BaseModel):
    reviewer_name: str = Field(..., min_length=2, max_length=128)
    reviewer_designation: str = Field(..., min_length=2, max_length=128)
    reviewer_organization: Optional[str] = Field(default="SCSS Forensic Laboratory", max_length=128)
    decision: str = Field(..., description="Decision: pending, requires_further_examination, reviewed_no_indicators, reviewed_manipulation_suspected, reviewed_inconclusive")
    notes: str = Field(..., min_length=5, description="Forensic examiner case notes")
    attestation: bool = Field(..., description="Explicit examiner attestation confirmation")


class HumanReviewResponse(BaseModel):
    status: str
    reviewer_name: Optional[str] = None
    reviewer_designation: Optional[str] = None
    reviewer_organization: Optional[str] = None
    notes: Optional[str] = None
    timestamp: Optional[datetime] = None
    attestation: bool = False


class ExaminationOverview(BaseModel):
    examination_id: str
    original_filename: str
    file_size_bytes: int
    detected_media_type: str
    sha256_digest: str
    upload_timestamp: datetime
    capture_timestamp: Optional[datetime] = None
    application_version: str
    analysis_pipeline_version: str
    image_width: int
    image_height: int
    color_mode: str
    status: str
    overall_assessment: str
    human_review_status: str


class ExaminationDetailResponse(BaseModel):
    examination_id: str
    status: str
    original_filename: str
    file_size_bytes: int
    detected_media_type: str
    image_width: int
    image_height: int
    color_mode: str
    upload_timestamp: datetime
    capture_timestamp: Optional[datetime] = None
    application_version: str
    analysis_pipeline_version: str

    file_integrity: FileIntegrityInfo
    tests: List[ScreeningTestResult]
    overall_assessment: str
    human_review_status: str
    human_review: HumanReviewResponse
    extracted_metadata: Dict[str, Any] = Field(default_factory=dict)
    known_limitations: List[str] = Field(default_factory=list)
    suggested_manual_checks: List[str] = Field(default_factory=list)
    artifacts: Dict[str, Any] = Field(default_factory=dict)
    activity_events: List[ActivityEventResponse] = Field(default_factory=list)
    report_generated_at: Optional[datetime] = None
    disclaimer: str


class IntegrityCheckResponse(BaseModel):
    examination_id: str
    stored_digest: str
    recomputed_digest: str
    match: bool
    algorithm: str = "SHA-256"
    checked_at: datetime
    status: str
    message: str


class DashboardStatsResponse(BaseModel):
    total_examinations: int
    recent_examinations_count: int
    pending_review_count: int
    reviewed_count: int
    requires_further_review_count: int
    reports_generated_count: int
    preliminary_notice: str
