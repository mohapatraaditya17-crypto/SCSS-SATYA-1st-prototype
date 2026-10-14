# SCSS SATYA — Scientific Limitations & Evidentiary Disclosures

## 1. Guiding Scientific Principle
> **"The absence of detected manipulation indicators does not establish that an image is authentic."**

In digital image forensics, proving a negative (i.e. proving that an image has NEVER been altered) is mathematically impossible from the pixel stream alone. A sophisticated actor can modify an image, strip metadata, perform optical re-sampling, and apply subtle gaussian blurring to suppress trace residuals.

---

## 2. Key Methodological Limitations

### A. Metadata Manipulation & Stripping
- **Vulnerability**: EXIF, IPTC, and XMP headers can be modified, edited, or completely wiped using standard command-line tools (e.g. `exiftool`) in seconds.
- **Social Media Behavior**: Messaging applications (WhatsApp, Signal, Telegram) and social networks (X, Facebook, Instagram) routinely strip metadata to protect user privacy and compress bandwidth.
- **Forensic Interpretation**: SATYA records missing metadata as *inconclusive*, not suspicious.

### B. Error Level Analysis (ELA) Nuances
- **Texture False Positives**: Natural high-contrast edges, fine textures (foliage, fabric, sand), and sharp text overlays naturally display elevated error levels under recompression without being tampered.
- **Re-Saving Suppression**: Re-saving an edited image multiple times at high quality homogenizes error levels across macroblocks, causing spliced regions to blend with background error levels.
- **Format Inapplicability**: ELA is mathematically meaningful solely for lossy discrete cosine transform (DCT) JPEG images. SATYA honestly identifies ELA as *test unavailable* for PNG and WebP files.

### C. Generative AI & Diffusion Models
- Modern deep generative models (Midjourney, DALL-E 3, Stable Diffusion, Flux) generate novel pixel distributions from text prompts without splicing existing JPEG macroblocks.
- Passive-blind screening methods that look for splicing seams or double-compression grids will not detect AI images unless synthetic frequency grid artifacts or explicit C2PA watermarks are present.
- SATYA explicitly disclaims being a universal deepfake detector.

### D. Cryptographic Hashes vs Source Authenticity
- A SHA-256 hash guarantees that stored bytes have not changed since the moment of acquisition.
- A hash does NOT prove that the image is an authentic depiction of reality. A completely fabricated deepfake image produces a valid SHA-256 digest just like any genuine photograph.

---

## 3. Prototype Status & Accreditation Disclosure

- **Prototype Stage**: SCSS SATYA is currently an early working prototype built for the SEVA FIRST Innovation Challenge 2026.
- **No Independent Accreditation**: This prototype has not undergone formal independent laboratory validation, ISO 17025 accreditation, or judicial admissibility certification.
- **Intended Use**: SATYA is intended exclusively for preliminary investigative triage to assist certified human examiners in prioritizing specimens for detailed laboratory hardware inspection.
