# Explainable Insurance Pricing Framework - Docker Startup Script (PowerShell)
# This script automates the build and startup of the system using Docker Compose.

Write-Host "[INFO] Initializing Explainable Insurance Pricing Framework..." -ForegroundColor Cyan

# Check if Docker is running
if (!(docker info 2>$null)) {
    Write-Host "[ERROR] Docker is not running. Please start Docker Desktop and try again." -ForegroundColor Red
    exit
}

# Clean up existing containers
Write-Host "[INFO] Cleaning up existing containers..." -ForegroundColor Yellow
docker-compose down

# Build and start services
Write-Host "[INFO] Building and starting services..." -ForegroundColor Green
Write-Host "Note: Initial run will pull llama3 (4GB), which may take several minutes."
docker-compose up --build -d

Write-Host "`n[SUCCESS] System services are starting up." -ForegroundColor Cyan
Write-Host "Management Dashboard: http://localhost:8501"
Write-Host "API Documentation:    http://localhost:8000/docs"
Write-Host "LLM Backend Stats:   http://localhost:11434"

Write-Host "`n[INFO] Tailing logs (Ctrl+C to stop viewing logs; containers will remain active)..." -ForegroundColor Gray
docker-compose logs -f
