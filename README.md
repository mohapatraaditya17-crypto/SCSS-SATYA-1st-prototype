# SCSS SATYA — Forensic Image Authenticity Screening Platform

> **Forensic-led digital image authenticity screening platform for authorized investigators, forensic laboratories, insurance claims teams, and digital trust institutions.**  
> Developed for **Sure Clue Scientific Solutions (SCSS)** • **SEVA FIRST Innovation Challenge 2026**  
> *Sector 9: Emerging Technologies (AI, Blockchain and Others)*  
> *Sub-theme 4: Responsible AI, Deepfake Detection, Cyber Resilience and Digital Trust*

---

## 🏛️ Guiding Forensic Doctrine
> **"The tool screens. The expert decides."**  
> Automated findings are never presented as conclusive forensic opinions, legal proof, or definitive proof that an image is authentic or manipulated.

SCSS SATYA rejects black-box unexplainable AI classifiers that produce arbitrary percentage scores (e.g., *"99% Fake"*). Instead, it implements a scientifically defensible **4-layer digital triage workflow** adhering to **ISO/IEC 27037:2012** and **Section 65B Indian Evidence Act 1872 / Section 63 Bharatiya Sakshya Adhiniyam (BSA) 2023**:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           SCSS SATYA WORKFLOW                               │
├─────────────────────────────────────────────────────────────────────────────┤
│  Layer 1: Passive-Blind Non-Invasive Manipulation Screening                │
│           • EXIF / IPTC / TIFF metadata inspection & software traces       │
│           • Error Level Analysis (ELA) with amplified residual heatmap      │
│           • Image geometry & spatial high-frequency noise variance          │
│                                                                             │
│  Layer 2: Tamper-Evident Evidence Integrity Record                         │
│           • SHA-256 cryptographic bitstream hashing directly from bytes    │
│           • Non-invasive raw byte preservation in evidence vault            │
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

## ✨ Core Capabilities

- **Institutional UI/UX Design System**: Deep SCSS Navy (`#0F1E36`), Refined Gold (`#C5A059`), and crisp laboratory aesthetics.
- **Interactive Visual Laboratory**:
  - Original evidence bitstream exhibit.
  - Error Level Analysis (ELA) heatmap exhibit with **interactive blend opacity slider**.
  - Dynamic RGB Color Channel saturation and standard deviation charts powered by **Recharts**.
- **Cryptographic Evidence Sealing**: Immediate SHA-256 hashing upon ingestion with live re-verification against stored vault bytes.
- **1-Click Calibrated Test Specimens**:
  - *Camera Photo*: Clean natural landscape with authentic Nikon D850 EXIF metadata.
  - *Spliced Composite*: Foreign spliced patch with Adobe Photoshop editing traces.
  - *Lossless PNG*: Demonstrates honest handling of formats where JPEG ELA is unavailable.
- **Official Forensic Reporting**:
  - Downloadable **ISO/IEC 27037 PDF Report** with two-pass dynamic page counter, embedded exhibits, and cryptographic hashes.
  - Structured, machine-readable **JSON Forensic Report**.
- **Evidence Vault Repository**: Searchable case history with filtering by case ID, filename, and review status.

---

## 🛠️ Technology Stack

| Layer | Technologies |
|---|---|
| **Frontend** | React 19, TypeScript, Vite, Tailwind CSS v4, Lucide Icons, Recharts, React Router v7 |
| **Backend** | Python 3.11+, FastAPI, Pydantic v2, Pillow, OpenCV (headless), ReportLab, ExifRead, SQLite, SQLAlchemy |
| **Testing** | pytest, FastAPI TestClient (httpx), synthetic test data generators |
| **Storage** | Local isolated storage: `vault/`, `artifacts/`, `reports/`, `satya_forensics.db` |

---

## 📁 Repository Structure

```
scss-satya/
├── backend/
│   ├── app/
│   │   ├── main.py               # FastAPI application & SPA mounting
│   │   ├── api/                  # API routers (health, examinations)
│   │   ├── core/                 # Config, security thresholds, constants
│   │   ├── schemas/              # Pydantic request & response models
│   │   ├── database/             # SQLite session & SQLAlchemy models
│   │   ├── services/             # Storage vault & audit activity logging
│   │   ├── analysis/             # Screening tests (Metadata, ELA, Consistency, Pipeline)
│   │   └── reports/              # ReportLab PDF & JSON report generators
│   ├── tests/                    # Automated pytest suite (16 tests)
│   ├── requirements.txt          # Python dependency specifications
│   └── Dockerfile                # Optional container image definition
├── frontend/
│   ├── src/
│   │   ├── components/           # Navbar, Footer, StatusBadges
│   │   ├── pages/                # Dashboard, NewExam, Results, History, Methodology
│   │   ├── services/             # API client service
│   │   ├── types/                # TypeScript interface definitions
│   │   ├── App.tsx               # Route declarations & layout
│   │   └── main.tsx              # React DOM mounting
│   ├── package.json              # Frontend npm dependencies
│   ├── vite.config.ts            # Vite build & API proxy configuration
│   └── dist/                     # Compiled production assets
├── storage/                      # Isolated local storage (Vault, Artifacts, Reports, DB)
├── docs/                         # Full architecture, API, security, methodology docs
│   ├── ARCHITECTURE.md
│   ├── API.md
│   ├── SECURITY.md
│   ├── METHODOLOGY.md
│   ├── TESTING.md
│   └── LIMITATIONS.md
├── scripts/                      # Startup, specimen generation & helper scripts
│   ├── run_backend.py
│   └── create_sample_images.py
├── docker-compose.yml            # Optional containerized orchestration
├── run.bat                       # 1-click Windows startup script
├── .env.example                  # Environment configuration template
├── .gitignore                    # Secrets & evidence vault exclusions
└── README.md                     # Project overview and documentation
```

---

## 🚀 Quick Start Guide

### 1. Prerequisites
- **Python 3.10+** (Tested on Python 3.11)
- **Node.js v18+** & **npm** (for frontend development/builds)
- Windows, macOS, or Linux

### 2. Setup Backend
Navigate to the `backend/` directory:
```bash
cd backend
pip install -r requirements.txt
```

### 3. Setup Frontend
Navigate to the `frontend/` directory and install dependencies:
```bash
cd ../frontend
npm install
npm run build
```

### 4. Launch Application

#### Option A: Unified Application (Recommended)
Run the backend server, which automatically serves the API, Swagger docs, and compiled frontend SPA:
```bash
python scripts/run_backend.py
```
*(On Windows, you can simply double-click `run.bat` at the repository root).*

#### Option B: Independent Development Servers
Run the backend in terminal 1:
```bash
cd backend
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
Run the Vite development server in terminal 2:
```bash
cd frontend
npm run dev
```

---

## 🌐 Application Access Endpoints

| Resource | URL | Description |
|---|---|---|
| **Forensic Web Dashboard** | 👉 **`http://127.0.0.1:8000/`** | Unified laboratory dashboard |
| **Interactive API Docs (Swagger)** | 👉 **`http://127.0.0.1:8000/docs`** | OpenAPI interactive UI |
| **ReDoc Technical Docs** | 👉 **`http://127.0.0.1:8000/redoc`** | ReDoc API specifications |
| **Health Endpoint** | 👉 **`http://127.0.0.1:8000/api/health`** | Engine status & manifest |
| **Vite Dev Server (Dev mode)** | 👉 **`http://localhost:5173/`** | Frontend hot-reloading dev server |

---

## 🧪 Automated Testing & Verification

Run the comprehensive 16-test backend test suite:
```bash
cd backend
python -m pytest tests/test_satya_backend.py -v
```

Execute the frontend type-check and production build:
```bash
cd frontend
npm run build
```

Generate synthetic sample images for testing:
```bash
python scripts/create_sample_images.py
```

---

## ⚠️ Scientific Limitations Disclosure
- **Preliminary Screening**: SCSS SATYA produces preliminary screening findings for investigative support. It does not provide legal proof or judicial determination of authenticity.
- **Negative Proof Infeasibility**: The absence of detected indicators does NOT establish that an image is authentic or unaltered.
- **Social Media Stripping**: Web messaging platforms routinely compress images and strip EXIF metadata for privacy; missing metadata is recorded as *inconclusive*.
- **Passive Generative AI Limits**: Deep diffusion models (Midjourney, DALL-E) cannot be reliably detected by splicing algorithms without watermarks or frequency artifacts.
- **Prototype Status**: This software is an experimental prototype and has not undergone formal ISO 17025 laboratory accreditation.
