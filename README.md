# Security RAG API 🛡️

> AI-powered security knowledge base API providing instant access to MITRE ATT&CK framework data through natural language queries.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/docker-ready-brightgreen.svg)](https://www.docker.com/)
[![MITRE ATT&CK](https://img.shields.io/badge/MITRE-ATT%26CK-red.svg)](https://attack.mitre.org/)

## 🎯 Overview

Security RAG API is a lightweight, containerized REST API that enables security teams to query the complete MITRE ATT&CK framework using natural language. Built for SOC analysts, threat hunters, and security engineers who need instant access to detection strategies, threat intelligence, and security best practices.

### Key Features

- 🔍 **Natural Language Queries** - Ask questions in plain English
- 🤖 **Local LLM Inference** - Powered by Ollama + TinyLLama (runs on-premise)
- 📊 **Vector Search** - ChromaDB for semantic similarity matching
- 🚀 **Single-Command Deploy** - Docker container with everything included
- 🔌 **Easy Integration** - REST API works with SIEM, SOAR, Slack, and more
- 📖 **Auto-Generated Docs** - Interactive Swagger UI at `/docs`
- 🔒 **Privacy-First** - All data stays on your infrastructure

## 🚀 Quick Start

### Prerequisites

- Docker 20.10+
- Ollama (running locally)
- 4GB RAM minimum
- 10GB disk space

### Installation

```bash
# 1. Ensure Ollama is running and configured
export OLLAMA_HOST=0.0.0.0:11434
ollama serve

# Pull TinyLlama model
ollama pull tinyllama

# 2. Clone this repository
git clone https://github.com/yourusername/security-rag-api.git
cd security-rag-api

# 3. Build the Docker image
docker build -t security-rag-api .

# 4. Run the container
docker run -d \
  --name security-rag \
  -p 8000:8000 \
  -v chroma_data:/data \
  -e OLLAMA_HOST=http://host.docker.internal:11434 \
  --add-host=host.docker.internal:host-gateway \
  security-rag-api

# 5. Load MITRE ATT&CK data (takes ~60 seconds)
curl -X POST http://localhost:8000/load-mitre

# 6. Verify it's working
curl http://localhost:8000/health
```

### First Query

```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "How to detect credential dumping?"}'
```

**Response:**
```json
{
  "question": "How to detect credential dumping?",
  "answer": "To detect credential dumping, monitor for: 1) Access to LSASS process memory...",
  "sources": 3
}
```

## 📚 API Documentation

### Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check and status |
| `/ask` | POST | Ask a security question |
| `/load-mitre` | POST | Load MITRE ATT&CK data |
| `/stats` | GET | Get knowledge base statistics |
| `/docs` | GET | Interactive API documentation |

### Interactive Documentation

Visit `http://localhost:8000/docs` for full Swagger UI documentation.

### Example Requests

**Ask about a technique:**
```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What is T1003.001?"}'
```

**Get detection strategies:**
```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "How to detect PowerShell abuse?"}'
```

**Check statistics:**
```bash
curl http://localhost:8000/stats
```

## 🔧 Integration Examples

### Python Client

```python
import requests

class SecurityRAG:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
    
    def ask(self, question):
        response = requests.post(
            f"{self.base_url}/ask",
            json={"question": question}
        )
        return response.json()["answer"]

# Usage
rag = SecurityRAG()
answer = rag.ask("How to detect mimikatz?")
print(answer)
```

### Bash CLI Tool

```bash
#!/bin/bash
# Save as 'sec-ask'

curl -s -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d "{\"question\": \"$1\"}" | jq -r '.answer'

# Usage: ./sec-ask "detect ransomware"
```

### Splunk Alert Action

```python
import requests
import os

def enrich_alert(alert_data):
    """Enrich security alert with MITRE context"""
    question = f"Detection methods for {alert_data['technique_id']}"
    
    response = requests.post(
        f"{os.getenv('SECURITY_RAG_API')}/ask",
        json={"question": question},
        timeout=5
    )
    
    return response.json()["answer"]
```

### Slack Bot

```python
from slack_bolt import App
import requests

app = App(token=os.environ["SLACK_BOT_TOKEN"])

@app.command("/security")
def handle_security_query(ack, command, say):
    ack()
    
    response = requests.post(
        "http://security-rag:8000/ask",
        json={"question": command["text"]}
    )
    
    say(f"🔒 *Security Intel:*\n{response.json()['answer']}")

# Usage: /security how to detect lateral movement
```

## 🏗️ Architecture

```
┌─────────────────┐      ┌──────────────────┐      ┌─────────────────┐
│                 │      │                  │      │                 │
│  Security Tool  │─────▶│  Security RAG    │─────▶│     Ollama      │
│  (SIEM/SOAR)   │      │      API         │      │   (TinyLlama)   │
│                 │      │                  │      │                 │
└─────────────────┘      └──────────────────┘      └─────────────────┘
                                 │
                                 │
                                 ▼
                         ┌──────────────────┐
                         │                  │
                         │    ChromaDB      │
                         │  (Vector Store)  │
                         │                  │
                         └──────────────────┘
                                 │
                                 │
                         ┌──────────────────┐
                         │  MITRE ATT&CK    │
                         │    Framework     │
                         └──────────────────┘
```

## 🎨 Use Cases

### SOC Operations
- **Alert Enrichment**: Automatically add MITRE context to security alerts
- **Incident Response**: Quick lookup of detection/response procedures during active incidents
- **Shift Handoffs**: Generate briefings on techniques observed during shift

### Threat Hunting
- **Hypothesis Generation**: Natural language queries for hunting ideas
- **TTP Research**: Quick access to adversary tactics and techniques
- **Hunt Query Builder**: Generate detection queries based on techniques

### Detection Engineering
- **Detection Gap Analysis**: Identify uncovered attack techniques
- **Rule Development**: Research detection strategies for new techniques
- **Data Source Mapping**: Understand required telemetry for detection

### Security Training
- **Junior Analyst Onboarding**: Self-service learning about techniques
- **Purple Team Exercises**: Quick reference for attack/defense scenarios
- **Certification Prep**: Interactive study tool for security certifications

## 🛠️ Development

### Project Structure

```
security-rag-api/
├── Dockerfile              # Container definition
├── main.py                # FastAPI application
├── requirements.txt       # Python dependencies
├── README.md             # This file
└── .gitignore           # Git ignore rules
```

### Local Development (without Docker)

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run locally
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Running Tests

```bash
# Install test dependencies
pip install pytest httpx

# Run tests
pytest
```

## 🔧 Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `OLLAMA_HOST` | `http://host.docker.internal:11434` | Ollama server URL |
| `MODEL_NAME` | `tinyllama` | LLM model to use |
| `LOG_LEVEL` | `INFO` | Logging level |

### Using Different Models

```bash
# Pull a more capable model
ollama pull llama2

# Update main.py or set environment variable
docker run -d \
  --name security-rag \
  -p 8000:8000 \
  -e MODEL_NAME=llama2 \
  security-rag-api
```

## 🐛 Troubleshooting

### Ollama Connection Issues

**Problem**: Health check shows `"ollama": "disconnected"`

**Solution**:
```bash
# Make sure Ollama listens on all interfaces
export OLLAMA_HOST=0.0.0.0:11434
ollama serve

# Verify from container
docker exec security-rag curl http://host.docker.internal:11434/api/tags
```

### Linux Host Networking

**Problem**: `host.docker.internal` not working on Linux

**Solution**:
```bash
# Find Docker bridge IP
ip addr show docker0 | grep "inet\b" | awk '{print $2}' | cut -d/ -f1

# Use actual IP (usually 172.17.0.1)
docker run -d \
  --name security-rag \
  -p 8000:8000 \
  -e OLLAMA_HOST=http://172.17.0.1:11434 \
  security-rag-api
```

### Slow Response Times

**Solutions**:
1. Upgrade to a faster model (llama2, mistral)
2. Use GPU acceleration with Ollama
3. Increase Docker memory allocation
4. Reduce `n_results` in queries

## 📊 Performance

| Metric | Value |
|--------|-------|
| Average Query Time | 2-5 seconds |
| Techniques Loaded | ~700+ |
| Memory Usage | ~2GB |
| Disk Space | ~5GB |
| Concurrent Requests | 10+ |

*Performance varies based on hardware and model selection*

## 🔒 Security Considerations

- **API Authentication**: Add API key authentication for production deployments
- **Rate Limiting**: Implement rate limiting to prevent abuse
- **Network Isolation**: Run in isolated network segment
- **Data Privacy**: Don't ingest sensitive internal data without proper controls
- **HTTPS**: Use reverse proxy (nginx/traefik) with TLS certificates
- **Input Validation**: All inputs are validated via Pydantic models

## 🗺️ Roadmap

- [ ] Add API key authentication
- [ ] Support for multiple MITRE matrices (Mobile, ICS)
- [ ] Integration with CVE/NVD databases
- [ ] Custom knowledge base ingestion
- [ ] Query result caching
- [ ] Multi-model support
- [ ] Grafana dashboard for analytics
- [ ] Kubernetes Helm chart

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.