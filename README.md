# Seoulholic Clinic AI Chatbot

Production-ready LINE chatbot with RAG and vision capabilities.

## Features

- RAG Pipeline (LlamaIndex + ChromaDB)
- Redis Caching Layer
- GPT-4o Vision Service
- Input Guard System
- Test Suite (1000+ cases)

## Quick Start

```bash
pip install -r requirements.txt
cp .env.example .env
./run_tests.sh
docker-compose up -d
```

## Performance

- Accuracy: 85-95%
- Latency: <3s
- Cache Hit: 60-80%

## License

MIT
