@echo off
cd /d "%~dp0"
echo Installing packages...
py -m pip install anthropic beautifulsoup4 python-dotenv requests lxml --quiet
echo.
echo Generating blog post...
echo.
py generate_now.py
echo.
echo Done! Check the output folder.
pause
