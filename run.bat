@echo off
echo ======================================================================
echo   SCSS SATYA — Forensic Image Authenticity Screening Platform
echo   Launching Unified Application Server on http://127.0.0.1:8000
echo ======================================================================
cd /d "%~dp0"
python scripts\run_backend.py
pause
