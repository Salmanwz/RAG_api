# Dockerfile
FROM python:3.11-slim
WORKDIR /app
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

RUN mkdir -p db

COPY app.py . 

COPY /tmp/attack.json ./tmp/attack.json

RUN pip install fastapi uvicorn chromadb ollama mitreattack-python requests

EXPOSE 8000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
