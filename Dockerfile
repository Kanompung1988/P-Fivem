# Dockerfile สำหรับ Phase 1 Upgrade
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements_upgrade.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements_upgrade.txt

# Copy application
COPY . .

# Create directories
RUN mkdir -p /app/chroma_db /app/data/text

# Expose ports
EXPOSE 8501 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD curl -f http://localhost:8501 || exit 1

# Default command (Streamlit)
CMD ["streamlit", "run", "streamlit_demo/app.py", "--server.port=8501", "--server.address=0.0.0.0"]
