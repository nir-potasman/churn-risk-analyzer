# Stampli Churn Risk Analyzer

Multi-agent system that analyzes Gong call transcripts to assess customer churn risk.

## Quick Start (Local)

```bash
# Copy environment template
cp .env.example .env
# Edit .env with your credentials

# Start all services
docker-compose up -d --build

# Open UI
open http://localhost:3000
```

## Architecture

| Service | Port | Purpose |
|---------|------|---------|
| Frontend | 3000 | Chat UI |
| Manager | 8080 | Orchestrates workflow |
| Transcript | 8001 | Fast DB access (no LLM) |
| Churn | 8002 | LLM-powered analysis |

## ECS Deployment

```bash
# Set your ECR registry
export ECR_REGISTRY=123456789.dkr.ecr.eu-west-1.amazonaws.com
export IMAGE_TAG=v1.0.0

# Build and push images
./deploy/build-and-push.sh

# Deploy using task definition
# See deploy/ecs-task-definition.json
```

## Documentation

See `AI_CONTEXT.md` for detailed technical documentation.

## Project Structure

```
├── agents/           # Core agent logic
├── frontend/         # Chat UI (FastAPI + Jinja2)
├── services/         # Dockerfiles + dependencies per service
├── deploy/           # ECS task definitions & scripts
└── compose.yaml      # Local development
```
