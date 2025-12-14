# Stampli Churn Analyzer

A multi-agent system for analyzing churn risk using AWS Bedrock and Redshift.

## Prerequisites

- Docker and Docker Compose
- AWS Credentials with Bedrock and Redshift access
- (Optional) Langfuse account for observability

## Quick Start

1. **Clone the repository**

2. **Configure Environment Variables**
   
   Copy the example environment file:
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and fill in your credentials:
   - AWS credentials (`AWS_ACCESS_KEY_ID`, etc.)
   - Redshift connection details (`REDSHIFT_HOST`, etc.)
   - Langfuse keys (`LANGFUSE_PUBLIC_KEY`, `LANGFUSE_SECRET_KEY`, `LANGFUSE_HOST`) - Required for observability


3. **Run with Docker Compose**

   Build and start the services:
   ```bash
   docker-compose up --build
   ```

   This will start:
   - Backend API at http://localhost:8000
   - Frontend UI at http://localhost:3000

4. **Access the Application**

   Open your browser to [http://localhost:3000](http://localhost:3000) and start chatting with the agent.

## Project Structure

- `backend/`: Python FastAPI application with LangGraph agent
- `frontend/`: React + TypeScript application
- `docker-compose.yml`: Orchestration for local development

## Development

### Backend
The backend uses `uv` for dependency management. To add dependencies:
```bash
cd backend
uv pip install package_name
# Update pyproject.toml manually to persist
```

### Frontend
The frontend uses Vite. To install dependencies:
```bash
cd frontend
npm install
```

## Deployment

The project is structured to be deployed on AWS ECS. Each service (backend, frontend) has its own Dockerfile and can be built and pushed to ECR independently.

