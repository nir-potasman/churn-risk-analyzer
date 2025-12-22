# Stampli Churn Risk Analyzer

Multi-agent system that analyzes Gong call transcripts to assess customer churn risk.

## Quick Start

```bash
# Start all services
docker-compose up -d --build

# Open UI
open http://localhost:8000
```

## Architecture

- **Frontend** (8000): Chat UI
- **Manager** (8080): Orchestrates workflow
- **Transcript Retriever** (8001): Fast DB access
- **Churn Analyzer** (8002): LLM analysis

## Documentation

See `AI_CONTEXT.md` for detailed technical documentation.

