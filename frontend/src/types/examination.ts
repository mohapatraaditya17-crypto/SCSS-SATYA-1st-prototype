export interface FileIntegrityInfo {
  algorithm: string;
  digest: string;
  sha1?: string;
  md5?: string;
  verified?: boolean;
}

export interface ScreeningTestResult {
  method: string;
  version: string;
  status: 'completed' | 'not_applicable' | 'failed';
  indicator: 'indicator_detected' | 'no_indicator_detected' | 'inconclusive' | 'test_unavailable' | 'test_failed';
  indicator_label: string;
  observations: string[];
  explanation: string;
  limitations: string[];
  execution_time_ms: number;
}

export interface ActivityEvent {
  id: number;
  event_type: string;
  timestamp: string;
  details: Record<string, any>;
}

export interface HumanReview {
  status: 'pending' | 'requires_further_examination' | 'reviewed_no_indicators' | 'reviewed_manipulation_suspected' | 'reviewed_inconclusive';
  reviewer_name?: string | null;
  reviewer_designation?: string | null;
  reviewer_organization?: string | null;
  notes?: string | null;
  timestamp?: string | null;
  attestation: boolean;
}

export interface ExaminationDetail {
  examination_id: string;
  status: string;
  original_filename: string;
  file_size_bytes: number;
  detected_media_type: string;
  image_width: number;
  image_height: number;
  color_mode: string;
  upload_timestamp: string;
  capture_timestamp?: string | null;
  application_version: string;
  analysis_pipeline_version: string;

  file_integrity: FileIntegrityInfo;
  tests: ScreeningTestResult[];
  overall_assessment: string;
  human_review_status: string;
  human_review: HumanReview;
  extracted_metadata: Record<string, any>;
  known_limitations: string[];
  suggested_manual_checks: string[];
  artifacts: Record<string, any>;
  activity_events: ActivityEvent[];
  report_generated_at?: string | null;
  disclaimer: string;
}

export interface ExaminationOverview {
  examination_id: string;
  original_filename: string;
  file_size_bytes: number;
  detected_media_type: string;
  sha256_digest: string;
  upload_timestamp: string;
  capture_timestamp?: string | null;
  application_version: string;
  analysis_pipeline_version: string;
  image_width: number;
  image_height: number;
  color_mode: string;
  status: string;
  overall_assessment: string;
  human_review_status: string;
}

export interface DashboardStats {
  total_examinations: number;
  recent_examinations_count: number;
  pending_review_count: number;
  reviewed_count: number;
  requires_further_review_count: number;
  reports_generated_count: number;
  preliminary_notice: string;
}

export interface IntegrityCheckResult {
  examination_id: string;
  stored_digest: string;
  recomputed_digest: string;
  match: boolean;
  algorithm: string;
  checked_at: string;
  status: string;
  message: string;
}
