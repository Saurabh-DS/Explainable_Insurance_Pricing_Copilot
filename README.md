# Explainable Insurance Pricing Copilot 🛡️

**A portable, production-grade AI system that runs anywhere with Docker.**

A production-grade local project demonstrating how to explain ML-based insurance premiums using RAG, SHAP, and AI Agents.

## 🌟 Overview

Insurance pricing is moving from rigid rule-based systems to complex ML models. However, "black-box" pricing is a regulatory and customer trust nightmare. This project solves that by providing a **Copilot** that explains every quote.

## 🏗️ Architecture

```text
+-------------------+       +-------------------+       +-------------------+
|   Customer Profile| ----> |   Pricing Model   | ----> |   SHAP Explainer  |
+-------------------+       |   (LightGBM)      |       | (Feature Impact)  |
                            +-------------------+       +-------------------+
                                      |                           |
                                      v                           v
+-------------------+       +-------------------+       +-------------------+
|   SQLite (Quotes) | <---- |   MCP Server      | ----> |   ChromaDB (RAG)  |
| (Similar Cases)   |       | (Tool Layer)      |       | (Guidelines)      |
+-------------------+       +-------------------+       +-------------------+
                                      |
                                      v
                            +-------------------+
                            |   LangGraph Agent |
                            |   (Ollama Llama3) |
                            +-------------------+
                                      |
                                      v
                            +-------------------+
                            | Final Explanation  |
                            +-------------------+
```

## 🚀 Features

- **ML Pricing**: LightGBM model trained on synthetic insurance data.
- **Explainability (SHAP)**: Identifies exactly how much each feature (age, vehicle group, etc.) added or subtracted from the base premium.
- **RAG (Retrieval Augmented Generation)**: Searches actual underwriting guidelines to provide context for the ML decisions.
- **MCP (Model Context Protocol)**: Modular tool layer exposing pricing and search capabilities.
- **Agentic Orchestration**: LangGraph manages the flow between tools to synthesize a final explanation.

## 🛠️ Setup (Beginner's Guide)

### 1. Ollama & Llama3 (The AI Brain)
Ollama allows you to run large language models locally on your machine.
- **Download**: Visit [ollama.com](https://ollama.com) and download the version for Windows.
- **Install**: Run the installer and ensure the Ollama icon appears in your system tray.
- **Pull Model**: Open Git Bash or PowerShell and run:
  ```bash
  ollama pull llama3
  ```
- **Verify**: Run `ollama list` to ensure `llama3` is available.

> [!TIP]
> **Git Bash "Command Not Found" Fix**:
> If Git Bash says `ollama: command not found`, run this command in your Git Bash terminal to link it:
> ```bash
> alias ollama='"/c/Users/$USER/AppData/Local/Programs/Ollama/ollama.exe"'
> ```
> Or simply use **PowerShell** or **Command Prompt**, as they usually pick up the Ollama path automatically.

### 3. Web UI (FastAPI + Streamlit) - RECOMMENDED 🌐
The modern way to use the app with a beautiful browser-based dashboard.
- **Install**: Download [Docker Desktop](https://www.docker.com/products/docker-desktop/).
- **Run Everything**:
  ```bash
  docker-compose up --build
  ```
- **Access the UI**: Open [http://localhost:8501](http://localhost:8501) in your browser.
- **Access the API**: Check [http://localhost:8000/docs](http://localhost:8000/docs) for the interactive Swagger documentation.

---

### 4. Local Execution (CLI Only)
1. **Git Bash Command**:
   ```bash
   chmod +x run_all.sh
   ./run_all.sh
   ```
2. **PowerShell Command**:
   ```powershell
   ./run_all.ps1
   ```

### 3. Containerization (Docker Compose) - NEW 🐳
The easiest way to run the full stack (App + Ollama) without installing anything else.
- **Install**: Download [Docker Desktop](https://www.docker.com/products/docker-desktop/).
- **Run Everything**:
  ```bash
  docker-compose up --build
  ```
- **What happens**: 
    - One container starts your insurance application.
    - Another container starts **Ollama** and automatically pulls **Llama3**.
    - They communicate over a secure internal network.
- **Interactivity**: Since the app takes user input, run it with:
    ```bash
    docker-compose run insurance-app
    ```

### 4. CI/CD (GitHub Actions)
This project includes a `.github/workflows/ci.yml` file. 
- **What it does**: Every time you `git push` to GitHub, a virtual machine automatically:
    1. Installs Python.
    2. Runs data generation.
    3. Trains the ML model.
    4. Verifies the Docker build.
- **How to see it**: Go to the "Actions" tab on your GitHub repository.

## 🌍 Instant Portability: Running on Other Systems

Yes! Because it is containerized, anyone can run your project without installing Python, ML libraries, or Ollama manually.

### 🏁 User Checklist (for your friend/colleague):
1.  **Install Docker Desktop**: They just need [Docker](https://www.docker.com/products/docker-desktop/).
2.  **Clone your Repo**: 
    ```bash
    git clone <your-repo-link>
    cd Explainable_Insurance_Pricing_Copilot
    ```
3.  **One Command to Rule Them All**:
    ```bash
    docker-compose up --build
    ```

### 🧠 Why this works:
- **Zero Python Setup**: Docker handles the Python version and all 15+ libraries.
- **Zero Database Setup**: SQLite and ChromaDB are initialized inside the container.
- **Zero AI Setup**: The `ollama-service` container automatically pulls `llama3` from the internet on its first run.
- **Everything Included**: Guidelines, training data, and the web UI are packaged together.

---

## 📄 Documentation

- [Architecture In-Depth](docs/architecture.md)
- [Interview Q&A](docs/interview_qa.md)
- [Deployment & CD Guide](docs/deployment.md)
