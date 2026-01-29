# Deployment & Continuous Deployment (CD) Guide

## 1. What is Continuous Deployment?
While **Continuous Integration (CI)** ensures your code builds and passes tests, **Continuous Deployment (CD)** automatically pushes those successful builds to a production environment.

In this project, CD means:
1.  Code is pushed to GitHub.
2.  CI tests pass.
3.  A new Docker image is automatically built.
4.  The image is pushed to a **Container Registry** (like GitHub Packages or Docker Hub).
5.  Your cloud provider pulls the new image and restarts the service.

---

## 2. Registry vs. Hosting: The "Warehouse" Analogy 🏗️
Think of your code like a **car**:
- **GitHub Registry (GHCR)**: This is the **Warehouse**. It stores the finished car (your Docker image) so it's ready to be shipped. It doesn't "drive" the car; it just keeps it safe and accessible.
- **Cloud Hosting (Service)**: This is the **Road**. To actually "drive" the car (run the app) so users can visit a URL like `app.com`, you have to "pull" the car out of the warehouse and put it on a cloud service.

## 3. How to "Drive" your App in the Cloud
To make your app a real website, you need one more step after pushing to GHCR:

### Step 1: Pick a "Road" (Host)
I recommend **Google Cloud Run** or **AWS App Runner**. They are designed to "listen" to your GitHub Warehouse.

### Step 2: Connect the Warehouse
You tell the Cloud Provider: *"Every time there is a new image in my GitHub Warehouse, please pull it and restart the website."*

### Step 3: Set up the Brain (LLM)
In the cloud, you can't easily run the Ollama container we used locally because it needs a very expensive GPU. 
- **The Pro Move**: Switch your project to use an **API** (like Google Gemini or OpenAI). 
- This makes your container tiny and makes the website fast and cheap to host.

---

## 4. Where can I deploy this project?

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

## 5. The "LLM Problem" in Production
This prototype uses **Ollama** (local). In a real production deployment:
- **Option 1 (Easiest)**: Switch the agent to use a hosted API like **Google Gemini**, **OpenAI**, or **Anthropic**. This eliminates the need to manage heavy GPUs.
- **Option 2 (Advanced)**: Deploy a GPU-enabled instance (e.g., AWS EC2 G-series) and run Ollama or vLLM inside it.

## 6. How to Run from GitHub Container Registry (GHCR)

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

## 7. The "Where is Ollama?" Quest

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

## 8. Deployment Check-list
1. [ ] Push code to GitHub (triggers CI/CD).
2. [ ] Verify image is in **GitHub -> Packages**.
3. [ ] Choose a Cloud Provider (e.g., Google Cloud Run).
4. [ ] Set Environment Variables (API Keys if switching from Ollama).
5. [ ] Deploy!
