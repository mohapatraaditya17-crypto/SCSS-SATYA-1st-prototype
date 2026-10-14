# SCSS SATYA — Application Security Architecture

## 1. Threat Model & Security Posture

SCSS SATYA is designed for forensic and investigative environments where evidentiary integrity and operational security are paramount. The application implements defense-in-depth measures against malicious payloads, input tampering, and accidental evidence corruption.

---

## 2. Evidence Ingestion Security Controls

### A. Magic Byte File Signature Verification
- The application never trusts client-supplied `Content-Type` headers or filename extensions.
- The first 12 bytes of every uploaded file are inspected:
  - **JPEG**: `0xFF 0xD8 0xFF`
  - **PNG**: `0x89 0x50 0x4E 0x47 0x0D 0x0A 0x1A 0x0A`
  - **WebP**: `RIFF` prefix with `WEBP` tag at offset 8.
- Non-compliant streams (executables, scripts, HTML) are rejected immediately.

### B. Decompression Bomb Mitigation
- To prevent denial-of-service via zip/decompression bombs, `Image.MAX_IMAGE_PIXELS` is strictly constrained to **50,000,000 pixels** (50 Megapixels).
- Images with dimensions exceeding this threshold or containing negative/infinite dimensions are rejected before allocating memory.

### C. File Size Enforcements
- A hard configurable limit of **15 MB** is enforced at the server layer.
- Files exceeding 15 MB are rejected with an explicit HTTP 400 response.

### D. Safe Server-Side File Identification & Path Traversal Protection
- Client-supplied filenames are never used as internal storage paths.
- Filenames are sanitized using `Path(original_filename).name`.
- Vault files are stored under UUID-based cryptographically randomized names (`{uuid4}_{sha256[:10]}.ext`).
- Path traversal sequences (`../`, `..\\`, encoded `%2F`) are stripped or blocked.

---

## 3. Evidence Preservation & Vault Isolation

- **Non-Invasive Preservation**: Raw uploaded bytes are written directly to `storage/vault/` without decompression or re-encoding.
- **Working Copy Analysis**: All screening tests (ELA, consistency, metadata extraction) operate on in-memory buffers or isolated copies.
- **Bitstream Integrity**: SHA-256 digests are computed directly from the ingested byte stream prior to any processing.
- **On-Demand Verification**: The `/api/examinations/{id}/integrity` endpoint re-hashes the stored vault bitstream on demand to verify that zero bit changes have occurred.

---

## 4. Privacy & Personal Data Protections

- **GPS Coordinate Redaction**: When EXIF geotagging tags are identified, exact numerical coordinates are redacted in automated summaries (`[REDACTED FOR PRIVACY: GPS Coordinate Data Present]`) to protect case privacy.
- **No External Exfiltration**: The platform operates completely locally without sending evidence to external AI classifiers, public cloud endpoints, or third-party APIs.

---

## 5. Prototype Storage vs Production Evidence Vault

> [!WARNING]
> **Local Prototype Storage Notice:** The local storage directories (`storage/vault/`, `storage/satya_forensics.db`) are suitable for prototype demonstration and testing on developer workstations. For production forensic laboratory deployment:
> - Storage volumes must be encrypted at rest (e.g., LUKS, BitLocker, AWS KMS).
> - Hardware Security Modules (HSMs) or PKI smartcards should manage examiner digital signatures.
> - Role-based access control (RBAC), multi-factor authentication (MFA), and off-site immutable write-once-read-many (WORM) backups must be implemented.
