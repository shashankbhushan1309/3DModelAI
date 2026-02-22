<#
.SYNOPSIS
    Sets up the AI CAD Copilot environment.
.DESCRIPTION
    Validates Node.js and Python installation, creates virtual environment, 
    and installs required dependencies.
#>

$ErrorActionPreference = "Stop"

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "   AI CAD Copilot Setup (Windows)         " -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

# 1. Check Python
Write-Host "`n[1/4] Checking Python..." -ForegroundColor Yellow
if (Get-Command "python" -ErrorAction SilentlyContinue) {
    $pyVer = (python --version)
    Write-Host "Found: $pyVer" -ForegroundColor Green
} else {
    Write-Host "Error: Python is not installed or not in PATH." -ForegroundColor Red
    exit 1
}

# 2. Check Node & NPM
Write-Host "`n[2/4] Checking Node.js and NPM..." -ForegroundColor Yellow
if (Get-Command "npm" -ErrorAction SilentlyContinue) {
    $nodeVer = (node -v)
    Write-Host "Found Node: $nodeVer" -ForegroundColor Green
} else {
    Write-Host "Error: NPM is not installed or not in PATH." -ForegroundColor Red
    exit 1
}

# 3. Setup Backend
Write-Host "`n[3/4] Setting up Backend Environment..." -ForegroundColor Yellow
cd backend
if (-Not (Test-Path "venv")) {
    Write-Host "Creating Virtual Environment..." -ForegroundColor Gray
    python -m venv venv
}
Write-Host "Activating Virtual Environment and Installing Dependencies..." -ForegroundColor Gray
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
cd ..
Write-Host "Backend setup complete." -ForegroundColor Green

# 4. Setup Frontend
Write-Host "`n[4/4] Setting up Frontend Environment..." -ForegroundColor Yellow
cd frontend
Write-Host "Installing NPM Packages..." -ForegroundColor Gray
npm install
cd ..
Write-Host "Frontend setup complete." -ForegroundColor Green

Write-Host "`n==========================================" -ForegroundColor Cyan
Write-Host "                SUCCESS!                  " -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "`nTo run the application, open TWO terminals:"
Write-Host "`nTerminal 1 (Backend):" -ForegroundColor Magenta
Write-Host "  cd backend"
Write-Host "  .\venv\Scripts\Activate.ps1"
Write-Host "  fastapi dev main.py"
Write-Host "`nTerminal 2 (Frontend):" -ForegroundColor Magenta
Write-Host "  cd frontend"
Write-Host "  npm run dev"
Write-Host "`nNote: Ensure Ollama is running ('ollama serve') and you have FreeCAD installed." -ForegroundColor Yellow
