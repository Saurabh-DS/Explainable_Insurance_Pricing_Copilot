# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Create necessary directories
RUN mkdir -p database logs pricing_model data/guidelines

# Run data generation and training as part of the build (or entrypoint)
# For production, you might want to mount these or run them separately
RUN python data_generation/generate_guidelines.py && \
    python data_generation/generate_quotes.py && \
    python pricing_model/train_model.py && \
    python rag/build_vector_store.py

# Expose ports for API (8000) and Streamlit (8501)
EXPOSE 8000
EXPOSE 8501

# No default CMD - will be specified in docker-compose
