# Deployment & Continuous Deployment (CD) Guide

## 1. What is Continuous Deployment?
While **Continuous Integration (CI)** ensures your code builds and passes tests, **Continuous Deployment (CD)** automatically pushes those successful builds to a production environment.

In this project, CD means:
1.  Code is pushed to GitHub.
2.  CI tests pass.
3.  A new Docker image is automatically built.
4.  The image is pushed to a **Container Registry** (like GitHub Packages or Docker Hub).
5.  Your cloud provider pulls the new image and restarts the service.

## 2. Where to Deploy?

Since this project is containerized, you have several excellent options:

### A. Google Cloud Run (Recommended)
- **Why**: Serverless, easy to use, and you only pay when the code is running.
- **Workflow**: GitHub Actions -> Google Artifact Registry -> Cloud Run.

### B. AWS App Runner
- **Why**: Fully managed service that maps directly to a GitHub repo or Docker image. Very scalable.

### C. Azure App Service for Containers
- **Why**: Great for enterprise environments with built-in monitoring and security.

### D. DigitalOcean App Platform
- **Why**: Very beginner-friendly and affordable fixed pricing.

## 3. The "LLM Problem" in Production
This prototype uses **Ollama** (local). In a real production deployment:
- **Option 1 (Easiest)**: Switch the agent to use a hosted API like **Google Gemini**, **OpenAI**, or **Anthropic**. This eliminates the need to manage heavy GPUs.
- **Option 2 (Advanced)**: Deploy a GPU-enabled instance (e.g., AWS EC2 G-series) and run Ollama or vLLM inside it.

## 4. How to Run from GitHub Container Registry (GHCR)

Once your CI/CD pipeline has pushed the image, anyone (or any server) with permission can run it using these commands:

1.  **Login** (required once per machine):
    ```bash
    export CR_PAT=YOUR_GITHUB_TOKEN
    echo $CR_PAT | docker login ghcr.io -u YOUR_GITHUB_USERNAME --password-stdin
    ```
2.  **Pull and Run**:
    ```bash
    docker run -it ghcr.io/YOUR_GITHUB_USERNAME/insurance-copilot:latest
    ```

---

## 5. The "Where is Ollama?" Quest

In a production environment (like AWS, Google Cloud, or even a local container), **Ollama is typically NOT inside your application container.** Here is why and how to handle it:

### Why not include Ollama in the Dockerfile?
- **Size**: Llama3 is several gigabytes. Including it makes the image huge and slow to deploy.
- **Hardware**: Ollama needs access to a GPU to be fast. Application containers are usually lightweight.

### Production Solution 1: Use a Hosted API (Recommended for Beginners) 🌟
Swap Ollama for an API that is already "always on."
- **Change**: In `agent/graph.py`, replace `ChatOllama` with `ChatGoogleGenerativeAI` or `ChatOpenAI`.
- **Benefit**: No servers to manage, no Ollama to install, instantly works in the cloud.

### Production Solution 2: Multi-Container (Docker Compose)
Run your app in one container and Ollama in another.
- **How**: Use a `docker-compose.yml` file to start both. 
- **Communication**: Your app talks to `ollama-service:11434` instead of `localhost`.

### Production Solution 3: Connect Docker to Host Ollama (Local Testing)
If you are running the Docker container locally and want to use the Ollama you already installed on Windows:
- **Windows/Mac Command**:
  ```bash
  docker run -it --add-host=host.docker.internal:host-gateway ghcr.io/username/insurance-copilot:latest
  ```
- **Code Change**: Tell your agent to look at `http://host.docker.internal:11434`.

---

## 6. Deployment Check-list
1. [ ] Push code to GitHub (triggers CI/CD).
2. [ ] Verify image is in **GitHub -> Packages**.
3. [ ] Choose a Cloud Provider (e.g., Google Cloud Run).
4. [ ] Set Environment Variables (API Keys if switching from Ollama).
5. [ ] Deploy!
