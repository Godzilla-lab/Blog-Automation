# Blog Automation System - PowerShell Runner
# Run this file by right-clicking and selecting "Run with PowerShell"

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "   BLOG AUTOMATION SYSTEM - AUTOMATED DEMO" -ForegroundColor Cyan
Write-Host "============================================================`n" -ForegroundColor Cyan

# Set location to script directory
Set-Location $PSScriptRoot

# Check if Python is available
Write-Host "Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ Python found: $pythonVersion`n" -ForegroundColor Green
} catch {
    Write-Host "❌ Python not found. Please install Python from python.org`n" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit
}

# Install dependencies
Write-Host "Installing dependencies (if needed)...`n" -ForegroundColor Yellow
python -m pip install --quiet anthropic beautifulsoup4 python-dotenv requests lxml 2>&1 | Out-Null

# Run automated demo
Write-Host "Starting automated blog generation...`n" -ForegroundColor Green
Write-Host "This will take 2-3 minutes. Please wait...`n" -ForegroundColor Yellow

python auto_generate.py

Write-Host "`n`n============================================================" -ForegroundColor Cyan
Write-Host "   Check the output folder for your generated content!" -ForegroundColor Cyan
Write-Host "============================================================`n" -ForegroundColor Cyan

Read-Host "Press Enter to exit"
