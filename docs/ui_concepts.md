# FastAPI vs. Streamlit: A Beginner's Guide

You asked for a UI using **FastAPI** and **Streamlit**. Here is how they work together in this project.

## 🧱 The Architecture: "The Brain and the Face"

We have separated the project into two distinct parts:

### 1. The Backend (FastAPI) - "The Brain"
- **What it is**: A high-performance web framework for building APIs.
- **Role**: It "hosts" the AI Agent, the ML Model, and the Database search logic.
- **Why we use it**: It is standard for production apps. It stays running 24/7, waiting for data. If we ever wanted to build a mobile app or a separate website, they would all talk to this same FastAPI backend.
- **Location**: `api/main.py`

### 2. The Frontend (Streamlit) - "The Face"
- **What it is**: A framework designed specifically for data science and AI UIs.
- **Role**: It creates the sliders, buttons, and text areas you see in your browser.
- **Why we use it**: It allows us to create a professional-looking dashboard in pure Python without needing to learn HTML, CSS, or JavaScript.
- **Location**: `ui/app.py`

---

## 📡 How they talk to each other
```text
[ YOU ] --- (Input) ---> [ Streamlit (Face) ]
                             |
                      (HTTP POST Request)
                             v
                       [ FastAPI (Brain) ] <---> [ AI Agent + ML ]
                             |
                      (JSON Response)
                             v
[ YOU ] <--- (Explanation) -- [ Streamlit (Face) ]
```

## 🐳 Why use Docker Compose for this?
Because we now have **three** separate servers running at once:
1.  **FastAPI** (Port 8000)
2.  **Streamlit** (Port 8501)
3.  **Ollama** (Port 11434)

Docker Compose acts as the manager that starts all three and connects them over a private internal network so they can "talk" to each other seamlessly.
