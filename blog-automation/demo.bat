@echo off
echo ============================================================
echo    BLOG AUTOMATION - AUTOMATED DEMO
echo    Generating blog post without user input
echo ============================================================
echo.
echo Installing dependencies (if needed)...
python -m pip install -q anthropic beautifulsoup4 python-dotenv requests lxml 2>nul
echo.
echo Starting automated generation...
echo.
python auto_generate.py
echo.
pause
