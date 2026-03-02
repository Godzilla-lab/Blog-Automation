@echo off
cd /d "%~dp0"
python -m pip install anthropic beautifulsoup4 python-dotenv requests lxml >nul 2>&1
cls
python generate_now.py
pause
