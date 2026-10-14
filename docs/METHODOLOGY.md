# SCSS SATYA — Forensic Screening Methodology

## 1. Guiding Scientific Doctrine
> **"The tool screens. The expert decides."**  
> Automated findings are never presented as conclusive forensic opinions, legal proof, or definitive proof that an image is authentic or manipulated.

SCSS SATYA implements a passive-blind, non-invasive digital triage pipeline. Passive-blind methods examine an image without requiring the original capturing camera or a reference copy of the scene.

---

## 2. Implemented Screening Methods

### Test A: File & Metadata Examination
- **Method Identifier**: `metadata_examination`
- **Version**: `1.0.0`
- **Scientific Foundation**: EXIF, IPTC, and TIFF metadata headers embedded by camera firmware contain records of device hardware, capture parameters, and editing tool signatures.
- **Implementation**:
  - Extracts camera Make, Model, Exposure Time, F-Number, ISO, Software, and Timestamps.
  - Compares the `Software` tag against known digital image processing, raster graphics, and generative AI tool signatures (e.g. Adobe Photoshop, GIMP, Canva, Stable Diffusion, Midjourney).
  - Flags positive indicators when editing software signatures are present.
  - Marks missing metadata as `inconclusive`, noting that metadata stripping is common behavior across web services and social platforms.

### Test B: SHA-256 Evidence Integrity Verification
- **Method Identifier**: `sha256_integrity`
- **Version**: `1.0.0`
- **Scientific Foundation**: Cryptographic hashing establishes a mathematical fingerprint of the evidence bitstream at the time of acquisition.
- **Implementation**:
  - Calculates 256-bit SHA-256, 160-bit SHA-1, and 128-bit MD5 digests directly from raw uploaded bytes.
  - Provides a re-verification endpoint that re-hashes the stored vault bitstream on demand.
  - Validates post-ingestion bitstream preservation in accordance with ISO/IEC 27037:2012.

### Test C: Error Level Analysis (ELA)
- **Method Identifier**: `error_level_analysis`
- **Version**: `1.0.0`
- **Scientific Foundation**: Lossy JPEG compression operates on 8x8 discrete cosine transform (DCT) macroblocks. An image uniformly compressed at a single quality level degrades at a uniform rate when re-saved at a known quality level (e.g. Q=90). When elements from foreign sources with different compression histories are pasted into an image, those regions degrade at disparate rates.
- **Implementation**:
  - Converts input JPEG to RGB, re-compresses to an in-memory buffer at Q=90, and calculates the absolute difference between original and re-compressed pixels.
  - Amplifies difference by a 15x scaling factor to generate a visible residual heatmap.
  - Computes quantitative residual metrics: mean error, standard deviation, and percentage of high-error pixels.
  - Strictly identifies the test as `test_unavailable` for lossless formats (PNG, WebP), preventing misleading artifacts.

### Test D: Basic Image Consistency Checks
- **Method Identifier**: `image_consistency_checks`
- **Version**: `1.0.0`
- **Scientific Foundation**: Real-world digital cameras capture natural optical scenes that exhibit consistent color channel saturation and uniform high-frequency sensor pattern noise (PRNU proxy).
- **Implementation**:
  - Evaluates color channel dynamic range, clipping, and mean/standard deviation per channel.
  - Applies a high-pass Laplacian filter to estimate high-frequency spatial noise across image quadrants.
  - Flags severe spatial noise asymmetry (e.g. ratio > 12:1) for manual examiner inspection.
  - Verifies that physical pixel dimensions match recorded EXIF dimension headers.

---

## 3. Evidentiary Standards Alignment

- **ISO/IEC 27037:2012**: Guidelines for identification, collection, acquisition, and preservation of digital evidence.
- **Section 65B Indian Evidence Act 1872 / Section 63 Bharatiya Sakshya Adhiniyam 2023**: Electronic record admissibility requirements.
- **SWGDE (Scientific Working Group on Digital Evidence)**: Best practices for forensic image analysis.
