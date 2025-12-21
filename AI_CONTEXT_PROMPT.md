# Churn Risk Analyzer - Project Overview for AI Context

## 1. Project Goal
The **Stampli Churn Risk Analyzer** is a multi-agent system designed to automatically assess the churn risk of customers by analyzing their Gong call transcripts stored in AWS Redshift.

When a user sends a request (e.g., "Analyze Vivo Infusion"), the system orchestrates agents to fetch call data, analyze conversation text for risk signals (competitor mentions, pricing complaints, etc.), and output a structured risk score and report.

## 2. Architecture & Tech Stack
*   **Framework**: Google ADK (Agent Development Kit) & A2A (Agent-to-Agent communication).
*   **Protocol**: A2A JSON-RPC Protocol (Method: `message/send`).
*   **Infrastructure**: Docker Compose (Microservices architecture).
*   **Database**: AWS Redshift (Cluster: `ai`, Database: `gong`).
*   **LLMs**: Claude 3.5 Sonnet (via Bedrock) for analysis; Claude Haiku for fast data retrieval.
*   **Tools**: `awslabs.redshift-mcp-server` (MCP - Model Context Protocol) for database access.

## 3. Agent Workflow (Microservices)
The system runs 3 specialized agents, each in its own Docker container:

### A. Account Manager Agent (Orchestrator)
*   **Active Code**: `agents/manager.py` (Used by `agents/apps/manager_app.py`)
*   **Port**: `8080`
*   **Role**: The entry point. It receives the user request, identifies the company name, and delegates the work to the Churn Risk Analyzer.
*   **URL**: `http://localhost:8080`

### B. Churn Risk Analyzer Agent (Analyst)
*   **Active Code**: `agents/churn_analyzer_agent.py` (Used by `agents/apps/churn_app.py`)
*   **Port**: `8002`
*   **Role**: The "Brain". It receives the company name, calls the Transcript Retriever to get the text, and then applies the **Scoring Rubric** (defined in `agents/prompts.py`) to calculate risk.

### C. Call Transcript Retriever Agent (Data Fetcher)
*   **Active Code**: `agents/call_transcripts_agent.py` (Used by `agents/apps/transcript_app.py`)
*   **Port**: `8001`
*   **Role**: The "Tool User". It connects to Redshift via MCP.
*   **Process**:
    1.  Queries `gong.calls` & `gong.call_accounts` to find the `call_id` for the company.
    2.  Queries `gong.call_transcripts` to fetch the text segments.
    3.  Formats the transcript into a readable string and returns it to the analyzer.

## 4. Key Files
*   **`agents/prompts.py`**: Centralized location for all agent system instructions and the **Risk Scoring Rubric** (Critical for understanding how risk is calculated).
*   **`agents/models.py`**: Pydantic models defining the input/output schemas (e.g., `ChurnRiskAssessment`).
*   **`config.py`**: Manages environment variables, AWS credentials, and model configuration.
*   **`compose.yaml`**: Defines the services and their networking.
*   **`agents/apps/*.py`**: The Starlette/FastAPI wrappers that expose the agents via the A2A protocol.

## 5. How to Run & Interact
The system is containerized.

1.  **Start the System**:
    ```bash
    docker compose up --build
    ```

2.  **Send a Request**:
    Use the A2A `message/send` protocol via `curl`:
    ```bash
    curl -v -X POST "http://localhost:8080/" \
      -H "Content-Type: application/json" \
      -d '{
        "jsonrpc": "2.0",
        "method": "message/send",
        "params": {
            "message": {
                "messageId": "msg-test-models",
                "role": "user",
                "parts": [{"text": "give me a churn risk analysis for vivo infusion"}]
            }
        },
        "id": 1
    }'
    ```

## 6. Known Issues / Notes
*   **Duplicate Folder Structure**: The repository contains both root-level agent files (`agents/churn_analyzer_agent.py`) and folder-based agents (`agents/churn_analyzer/agent.py`). The `apps/` currently import from the root-level files (except for `manager.py`). This should be cleaned up in future refactoring.
*   **Redshift Access**: The `transcript_retriever` relies on valid AWS credentials being passed to the container via `.env`.

