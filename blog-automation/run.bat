@echo off
echo Installing dependencies...
python -m pip install -r requirements.txt --quiet

echo.
echo Starting Blog Automation System...
echo.
python main.py

countinue
echo.
echo Blog Automation System has finished running.
echo.

