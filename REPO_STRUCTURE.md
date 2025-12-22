# Repository Structure: Churn Risk Analyzer

This repository contains a Google ADK multi-agent system designed to assess customer churn risk by analyzing Gong call transcripts stored in AWS Redshift.

## Directory Tree

```
/
├── agents/                       # Core Agent Logic & Components
│   ├── account_manager/          # Account Manager Agent (Orchestrator)
│   │   └── agent.py              # Agent definition
│   ├── churn_analyzer/           # Churn Risk Analyzer Agent
│   │   └── agent.py              # Agent definition (Analysis logic)
│   ├── transcript_retriever/     # Call Transcript Retriever Agent
│   │   └── agent.py              # Agent definition (Redshift Tools)
│   ├── apps/                     # A2A (Agent-to-Agent) Service Wrappers
│   │   ├── churn_app.py          # FastAPI/Starlette app for Churn Agent
│   │   ├── manager_app.py        # FastAPI/Starlette app for Manager Agent
│   │   └── transcript_app.py     # FastAPI/Starlette app for Transcript Agent
│   ├── manager.py                # Root Manager Agent definition (currently active)
│   ├── churn_analyzer_agent.py   # Root Churn Agent definition (currently active)
│   ├── call_transcripts_agent.py # Root Transcript Agent definition (currently active)
│   ├── models.py                 # Pydantic Data Models (Schemas)
│   └── prompts.py                # System Prompts & Scoring Rubrics
│
├── config.py                     # Configuration (Env vars, Model IDs, URLs)
├── compose.yaml                  # Docker Compose setup for multi-service deployment
├── Dockerfile                    # Container definition
├── PROJECT_BRIEF.md              # High-level project description
└── NEW_ARCHITECTURE.mermaid      # Diagram of the agent architecture
```

## Key Components

### 1. Agents (`agents/`)
The system consists of three specialized agents:

*   **Account Manager** (`agents/account_manager/` & `agents/manager.py`):
    *   **Role**: Orchestrator.
    *   **Function**: Receives user requests and delegates to the Churn Analyzer.
    *   **Type**: LLM Agent (Smart Model).

*   **Churn Risk Analyzer** (`agents/churn_analyzer/`):
    *   **Role**: Analyst.
    *   **Function**: Requests transcripts, analyzes text using rubrics, and outputs risk scores.
    *   **Type**: LLM Agent (Smart Model).

*   **Transcript Retriever** (`agents/transcript_retriever/`):
    *   **Role**: Data Fetcher.
    *   **Function**: Connects to AWS Redshift via MCP to query Gong call data.
    *   **Type**: Tool-Use Agent (Fast Model).

### 2. Applications (`agents/apps/`)
These files wrap the agents in **Google ADK's A2A (Agent-to-Agent)** framework, creating HTTP services that allow the agents to communicate with each other in a microservices architecture.

### 3. Shared Resources
*   **`agents/prompts.py`**: Centralized location for all agent system instructions and the churn risk scoring rubric.
*   **`agents/models.py`**: Defines the structured data objects (Pydantic models) passed between agents (e.g., `CallTranscript`, `ChurnRiskAssessment`).
*   **`config.py`**: Manages environment variables, AWS credentials, and model configuration.

