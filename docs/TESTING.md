# SCSS SATYA — Testing & Quality Assurance Guide

## 1. Overview
The SCSS SATYA prototype includes a comprehensive automated test suite covering backend API endpoints, file uploads, hashing accuracy, metadata extraction, ELA recompression, integrity verification, PDF generation, and frontend TypeScript build validation.

---

## 2. Automated Test Execution

### Backend Automated Test Suite (pytest)
Navigate to the `backend` directory and run pytest:
```bash
cd backend
python -m pytest tests/test_satya_backend.py -v
```

### Test Suite Coverage Matrix

| Test Case | Method / Endpoint | Verification Scope | Status |
|---|---|---|---|
| `test_health_endpoint` | `GET /api/health` | Service health, version manifest, vault access | **PASSED** |
| `test_version_endpoint` | `GET /api/version` | Platform manifest, method versions, disclaimer | **PASSED** |
| `test_sha256_hashing_correctness` | `POST /api/examinations` | Exact match against independent `hashlib.sha256` | **PASSED** |
| `test_valid_jpeg_upload` | `POST /api/examinations` | JPEG magic bytes, safe decode, ELA heatmap | **PASSED** |
| `test_valid_png_upload` | `POST /api/examinations` | PNG upload, ELA identified honestly as unavailable | **PASSED** |
| `test_unsupported_file_type` | `POST /api/examinations` | Non-image / binary payload rejection (HTTP 400) | **PASSED** |
| `test_corrupted_image_file` | `POST /api/examinations` | Truncated / malformed byte stream rejection (HTTP 400) | **PASSED** |
| `test_oversized_file_rejection` | `POST /api/examinations` | >15 MB file rejection enforcement (HTTP 400) | **PASSED** |
| `test_examination_history_and_retrieval` | `GET /api/examinations` | Case retrieval, pagination, search filtering | **PASSED** |
| `test_integrity_check` | `GET /api/examinations/{id}/integrity` | Accurate detection of matching and altered bitstreams | **PASSED** |
| `test_human_review_submission` | `POST /api/examinations/{id}/review` | Examiner attestation validation, note persistence | **PASSED** |
| `test_json_and_pdf_report_generation` | `GET /api/examinations/{id}/report.pdf` | Valid %PDF- stream, page counter, tables | **PASSED** |
| `test_path_traversal_protection` | `GET /api/examinations/..%2F..` | Path traversal stripping and 404 enforcement | **PASSED** |
| `test_dashboard_stats_endpoint` | `GET /api/dashboard/stats` | Accurate count aggregation from real DB records | **PASSED** |
| `test_visualization_and_image_endpoints` | `GET /api/.../visualizations/` | Serves original image and derived ELA heatmap | **PASSED** |
| `test_frontend_spa_serving` | `GET /` | Root route serves compiled React SPA index.html | **PASSED** |

---

## 3. Frontend Production Build Verification

To verify TypeScript type-safety and Vite bundling:
```bash
cd frontend
npm run build
```
Result: `tsc -b && vite build` completes with **0 errors**, emitting minified production assets in `frontend/dist/`.

---

## 4. Generating Synthetic Test Specimens

Run the specimen generator script to generate safe, synthetic test images:
```bash
python scripts/create_sample_images.py
```
This produces:
- `storage/samples/sample_authentic_camera.jpg`: Clean Nikon D850 camera specimen.
- `storage/samples/sample_tampered_composite.jpg`: Spliced composite with Adobe Photoshop EXIF metadata.
- `storage/samples/sample_lossless.png`: Lossless PNG specimen.
