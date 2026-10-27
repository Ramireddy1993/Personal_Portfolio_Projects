@echo off
echo Starting Resume Analyser Web App...
cd /d "%~dp0"
python -m streamlit run app.py
pause
