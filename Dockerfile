FROM python:3.11-slim

WORKDIR /app

# Install deps
COPY streamlit_demo/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# App code (will be overridden by volume mount in docker-compose for dev)
COPY streamlit_demo /app

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0", "--server.port=8501"]
