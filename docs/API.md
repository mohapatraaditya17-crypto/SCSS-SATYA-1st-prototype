# SCSS SATYA — REST API Specification

All endpoints communicate using standard JSON or binary streams. Timestamps are formatted in ISO-8601 UTC.

Base URL: `http://127.0.0.1:8000/api`  
Interactive OpenAPI UI: `http://127.0.0.1:8000/docs`

---

## 1. System Endpoints

### `GET /api/health`
Checks application health, active versions, and storage vault availability.

**Response (200 OK):**
```json
{
  "status": "healthy",
  "service": "SCSS SATYA",
  "version": "1.0.0",
  "pipeline_version": "2026.1",
  "vault_accessible": true,
  "core_principle": "The tool screens. The expert decides."
}
```

### `GET /api/version`
Returns the software version manifest, screening method versions, and standard compliance frameworks.

**Response (200 OK):**
```json
{
  "platform": "SCSS SATYA — Forensic Image Authenticity Screening Platform",
  "version": "1.0.0",
  "analysis_pipeline_version": "2026.1",
  "methods": {
    "metadata_examination": "1.0.0",
    "sha256_integrity": "1.0.0",
    "error_level_analysis": "1.0.0",
    "image_consistency_checks": "1.0.0"
  },
  "disclaimer": "SCSS SATYA produces preliminary...",
  "organization": "Sure Clue Scientific Solutions (SCSS)"
}
```

---

## 2. Examination Endpoints

### `POST /api/examinations`
Uploads and screens digital image evidence.

- **Content-Type**: `multipart/form-data`
- **Body Parameter**: `file` (Binary image stream; supported formats: JPEG, PNG, WebP; maximum size: 15 MB).

**Response (201 Created):**
```json
{
  "examination_id": "SATYA-20261014-A1B2C3",
  "status": "completed",
  "original_filename": "evidence.jpg",
  "file_size_bytes": 1048576,
  "detected_media_type": "image/jpeg",
  "image_width": 1920,
  "image_height": 1080,
  "color_mode": "RGB",
  "upload_timestamp": "2026-10-14T08:15:30Z",
  "capture_timestamp": "2026-10-12T14:22:10Z",
  "application_version": "1.0.0",
  "analysis_pipeline_version": "2026.1",
  "file_integrity": {
    "algorithm": "SHA-256",
    "digest": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    "sha1": "da39a3ee5e6b4b0d3255bfef95601890afd80709",
    "md5": "d41d8cd98f00b204e9800998ecf8427e",
    "verified": true
  },
  "tests": [
    {
      "method": "metadata_examination",
      "version": "1.0.0",
      "status": "completed",
      "indicator": "no_indicator_detected",
      "indicator_label": "No indicator detected by this test",
      "observations": ["Parsed 24 metadata headers"],
      "explanation": "Extracted metadata appears consistent...",
      "limitations": ["Metadata is easily manipulated or stripped..."],
      "execution_time_ms": 12.4
    }
  ],
  "overall_assessment": "requires_human_review",
  "human_review_status": "pending",
  "human_review": {
    "status": "pending",
    "attestation": false
  },
  "extracted_metadata": {},
  "known_limitations": [],
  "suggested_manual_checks": [],
  "artifacts": {
    "ela_heatmap": "SATYA-20261014-A1B2C3_ela.png"
  },
  "activity_events": [],
  "disclaimer": "..."
}
```

### `GET /api/examinations`
Lists historical examination records.

- **Query Parameters**:
  - `search` (string, optional): Search by Case ID, Filename, or SHA-256 hash.
  - `status` (string, optional): Filter by execution status (`completed`, `failed`).
  - `review_status` (string, optional): Filter by review status (`pending`, `reviewed_no_indicators`, etc.).
  - `sort_by` (string, default: `upload_timestamp`).
  - `order` (string, default: `desc`).
  - `limit` (integer, default: 50).
  - `offset` (integer, default: 0).

### `GET /api/examinations/{examination_id}`
Retrieves complete details of a specific examination case.

### `GET /api/examinations/{examination_id}/report`
Returns a machine-readable JSON forensic examination report.

### `GET /api/examinations/{examination_id}/report.pdf`
Generates and streams an ISO/IEC 27037 compliant PDF examination report with embedded exhibits and cryptographic seals.

### `GET /api/examinations/{examination_id}/integrity`
Recomputes the SHA-256 hash directly from the original stored vault bytes and verifies consistency against the recorded digest.

**Response (200 OK):**
```json
{
  "examination_id": "SATYA-20261014-A1B2C3",
  "stored_digest": "e3b0c442...",
  "recomputed_digest": "e3b0c442...",
  "match": true,
  "algorithm": "SHA-256",
  "checked_at": "2026-10-14T08:20:00Z",
  "status": "VERIFIED",
  "message": "Cryptographic integrity intact: bitstream matches recorded upload hash."
}
```

### `POST /api/examinations/{examination_id}/review`
Records certified human forensic examiner review and attestation.

**Request Body (JSON):**
```json
{
  "reviewer_name": "Dr. A. Dixit",
  "reviewer_designation": "Chief Forensic Examiner",
  "reviewer_organization": "Sure Clue Scientific Solutions",
  "decision": "reviewed_no_indicators",
  "notes": "Manual shadow consistency and edge inspection complete. No evidence of composite insertion.",
  "attestation": true
}
```

### `GET /api/examinations/{examination_id}/visualizations/{vis_type}`
Streams derived forensic visual artifacts (e.g. `ela_heatmap`, `noise_map`).

### `GET /api/examinations/{examination_id}/image`
Streams the original untouched evidence image safely from the vault.

### `GET /api/dashboard/stats`
Returns live operational metrics calculated directly from the local SQLite database.
