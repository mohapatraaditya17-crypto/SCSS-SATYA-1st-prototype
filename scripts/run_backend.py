import sys
import os
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

import uvicorn

if __name__ == "__main__":
    print("=" * 70)
    print("  SCSS SATYA — Forensic Image Authenticity Screening Platform")
    print("  Guiding Doctrine: 'The tool screens. The expert decides.'")
    print("=" * 70)
    print("  Backend API:    http://127.0.0.1:8000")
    print("  API Docs:       http://127.0.0.1:8000/docs")
    print("  Unified Web UI: http://127.0.0.1:8000/")
    print("=" * 70)
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
