# SCSS SATYA — System Architecture & Component Design

## 1. Guiding Doctrine
> **"The tool screens. The expert decides."**  
> Automated findings are never presented as conclusive forensic opinions, legal proof, or definitive proof that an image is authentic or manipulated.

---

## 2. 4-Layer Forensic Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           SCSS SATYA ARCHITECTURE                           │
├─────────────────────────────────────────────────────────────────────────────┤
│  Layer 1: Passive-Blind Non-Invasive Manipulation Screening                │
│           • EXIF / XMP / IPTC metadata inspection (Test A)                 │
│           • Error Level Analysis (ELA) with amplified residual map (Test C) │
│           • Image geometry & spatial high-frequency noise variance (Test D) │
│                                                                             │
│  Layer 2: Tamper-Evident Evidence Integrity Record                         │
│           • SHA-256 cryptographic bitstream hashing (Test B)                │
│           • Non-invasive raw byte storage in isolated vault                │
│           • On-demand bitstream re-verification endpoint                    │
│                                                                             │
│  Layer 3: Explainable Technical Findings & Limitations                      │
│           • Multi-indicator checklist (No Indicator / Indicator / Inconcl.)│
│           • Mandatory scientific limitations declaration                    │
│           • Suggested manual verification checklist for examiners           │
│                                                                             │
│  Layer 4: Qualified Human Forensic Review & Legal Certification             │
│           • Certified examiner credentials & formal qualitative notes       │
│           • Formal opinion attestation checkbox                             │
│           • Downloadable ISO/IEC 27037 PDF & machine-readable JSON reports  │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Component Interaction & Data Flow

```mermaid
sequenceDiagram
    autonumber
    actor Examiner as Forensic Examiner
    participant FE as React Frontend (Vite)
    participant API as FastAPI Router
    participant SEC as Storage & Security Service
    participant PIPE as Forensic Screening Pipeline
    participant DB as SQLite Evidence Database
    participant REP as PDF / JSON Report Generator

    Examiner->>FE: Select / Drag-and-drop Image
    FE->>FE: Validate file size (<15MB) & render safe preview
    Examiner->>FE: Confirm examination attestation
    FE->>API: POST /api/examinations (multipart/form-data)
    API->>SEC: Validate magic bytes (JPEG/PNG/WebP) & PIL decode check
    SEC->>SEC: Compute SHA-256 digest from original bitstream
    SEC->>SEC: Archive untouched bytes to storage/vault/
    API->>DB: Record initial case & write EXAMINATION_CREATED audit event
    API->>PIPE: Execute 4-Layer Screening Pipeline
    PIPE->>PIPE: Test A: File & EXIF Metadata Analysis
    PIPE->>PIPE: Test B: SHA-256 Cryptographic Integrity Reference
    PIPE->>PIPE: Test C: Error Level Analysis (ELA) on JPEG
    PIPE->>PIPE: Test D: Image Geometry & Noise Variance Analysis
    PIPE-->>API: Structured findings, limitations & derived exhibits
    API->>DB: Persist test results, metrics & audit trail
    API-->>FE: Return structured JSON ExaminationDetailResponse
    FE->>Examiner: Render Visual Laboratory (Original vs ELA, Charts, Tests)

    Examiner->>FE: Submit Human Review & Attestation
    FE->>API: POST /api/examinations/{id}/review
    API->>DB: Update human review status & append audit event
    API-->>FE: Return attested examination record

    Examiner->>FE: Request Official Forensic Report
    FE->>API: GET /api/examinations/{id}/report.pdf
    API->>REP: Build ReportLab PDF with Two-Pass Page Counter
    REP-->>API: Stream PDF with embedded exhibits & hashes
    API-->>Examiner: Download PDF Report
```

---

## 4. Storage Architecture

| Directory | Purpose | Security Policy |
|---|---|---|
| `storage/vault/` | Stores untouched original uploaded evidence bytes | Read-only working copy; never edited in place |
| `storage/artifacts/` | Stores derived visual exhibits (ELA heatmaps, noise maps) | Derived inspection outputs; clearly labelled as non-original |
| `storage/reports/` | Stores generated ISO/IEC 27037 PDF reports | Generated on-demand or cached for download |
| `storage/satya_forensics.db` | Relational SQLite database | Indexed by `examination_id` and `sha256_digest` |

---

## 5. Technology Stack Summary

- **Frontend**: React 19, TypeScript, Vite, Tailwind CSS v4, Lucide React, Recharts, React Router v7.
- **Backend**: Python 3.11, FastAPI, Pydantic v2, Pillow, OpenCV (headless), ReportLab, ExifRead, SQLite, SQLAlchemy.
- **Testing**: pytest, FastAPI TestClient (httpx), synthetic image generation scripts.
