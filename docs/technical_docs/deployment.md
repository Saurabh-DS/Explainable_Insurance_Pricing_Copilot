# Deployment & Operations Guide

## Container Strategy

This application is designed to be **Cloud-Agnostic**. It runs entirely within Docker containers, making it deployable on:
*   Local Developer Machines (Windows/Mac/Linux).
*   On-Premise Servers (Air-gapped environments).
*   Cloud VMs (AWS EC2, Azure VM, GCP Compute Engine).

### Docker Compose Services

1.  **`insurance-ui`**: The Streamlit frontend.
    *   Exposes Port: `8501`.
    *   Role: User traffic entry point.
2.  **`insurance-api`**: The FastAPI backend (optional, if coupled). *Note: In the current monolithic architecture, logic is imported directly for performance, but the container structure supports splitting.*
3.  **`ollama-backend`**: The Logic Inference Engine.
    *   Image: `ollama/ollama:latest`.
    *   Volume: `ollama_data` (Persists the downloaded models so you don't re-download 4GB on every restart).
    *   Exposes Port: `11434`.

## Deployment Checklist

### 1. Environment Setup
Ensure the host machine has **Docker Engine** and **Docker Compose** installed.
*   **Minimum Requirements**: 8GB RAM (16GB Recommended for Llama 3), 4 vCPUs.

### 2. Build & Launch
```bash
# 1. Clone Source
git clone https://github.com/your-org/pricing-copilot.git

# 2. Build Containers
docker-compose build

# 3. Start Services (Background Mode)
docker-compose up -d
```

### 3. Verification
Check service health:
```bash
docker ps
# Expected: insurance-ui (Up), ollama-backend (Up)
```

Access the application at `http://localhost:8501`.

## Continuous Integration (CI)

The included `.github/workflows/ci.yml` pipeline ensures code quality:
1.  **Linting**: Flake8/Black checks.
2.  **Unit Tests**: `pytest` runs against the Pricing Model logic.
3.  **Integration Tests**: Verifies that `docker build` succeeds.
4.  **End-to-End**: Runs a synthetic user query flow.

## Troubleshooting

**Issue**: "Ollama Connection Refused"
*   **Fix**: Ensure `OLLAMA_BASE_URL` env var in `docker-compose.yml` points to `http://ollama-backend:11434`, not `localhost`.

**Issue**: "Models not found"
*   **Fix**: The first startup pulls the model. Check logs with `docker logs ollama-backend`.
