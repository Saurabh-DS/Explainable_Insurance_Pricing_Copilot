Write-Host "Starting complete Docker environment cleanup..." -ForegroundColor Cyan

# 1. Stop and remove containers, networks, volumes, and images defined in the compose file
# This targets internal Docker metadata and resources only.
Write-Host "Stopping services and removing project-specific Docker artifacts..." -ForegroundColor Yellow
docker-compose down --rmi all --volumes --remove-orphans

Write-Host "Docker-specific cleanup complete! No project files were modified." -ForegroundColor Green
Write-Host "You can now run ./start_docker.ps1" -ForegroundColor Green
