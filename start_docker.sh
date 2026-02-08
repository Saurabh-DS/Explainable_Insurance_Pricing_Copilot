#!/bin/bash

# Explainable Insurance Pricing Framework - Docker Startup Script
# This script automates the build and startup of the system using Docker Compose.

echo "[INFO] Initializing Explainable Insurance Pricing Framework..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
  echo "[ERROR] Docker is not running. Please start Docker Desktop and try again."
  exit 1
fi

# Clean up existing containers
echo "[INFO] Cleaning up existing containers..."
docker-compose down

# Build and start services
echo "[INFO] Building and starting services..."
echo "Note: Initial run will pull llama3 (4GB), which may take several minutes."
docker-compose up --build -d

echo -e "\n[SUCCESS] System services are starting up."
echo "Management Dashboard: http://localhost:8501"
echo "API Documentation:    http://localhost:8000/docs"
echo "LLM Backend Stats:   http://localhost:11434"

echo -e "\n[INFO] Tailing logs (Ctrl+C to stop viewing logs; containers will remain active)..."
docker-compose logs -f
