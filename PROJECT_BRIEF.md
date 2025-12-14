# Project Brief: Multi-Agent Churn Risk Analyzer (ADK + MCP + Bedrock)

> **SYSTEM CONTEXT FOR AI ASSISTANT:**
> You are an expert AI software engineer. You are reading this brief to initialize a new project repository from scratch.
> Your goal is to build a Multi-Agent System using **Google's ADK** framework, but powered by **AWS Bedrock** models.
> **CRITICAL:** Use `uv` for all package management. Do not use `pip` or `venv` directly.

## 1. Executive Summary
We are building an agentic system to analyze "Churn Risk" for B2B customers. We will use **Google's Gen AI Agent Development Kit (ADK)** as the orchestration framework, but we will power the intelligence using **AWS Bedrock (Claude 3.5 Sonnet)** models.

The system uses the **Model Context Protocol (MCP)** to connect these agents to enterprise data sources like AWS Redshift. We will use the **ADK Web UI** for the frontend.

## 2. Core Technology Stack
-   **Orchestration Framework:** Google Gen AI Agent Development Kit (ADK).
-   **LLM Provider:** AWS Bedrock (Claude 3.5 Sonnet).
-   **Integration Protocol:** Model Context Protocol (MCP).
-   **Database Integration:** `awslabs/redshift-mcp-server` (running via `uvx`).
-   **Package Manager:** `uv` (Strict requirement).

## 3. Architecture: The "Agent Team"
The system follows a hierarchical **Manager-Worker** pattern utilizing the A2A (Agent-to-Agent) protocol provided by ADK.

### A. Root Agent: "The Account Manager"
-   **Role:** Interface with the user.
-   **Responsibility:** Understands the user's business question (e.g., "Why is Vivo Infusion at risk?"), delegates data retrieval to sub-agents, and presents the final report.
-   **Tools:** None direct. It relies on handing off tasks to sub-agents via ADK's A2A routing.

### B. Sub-Agent 1: "The Redshift Specialist"
-   **Role:** Retrieve structured data and call transcripts.
-   **Tooling:** Connected via **MCP** to AWS Redshift (`awslabs/redshift-mcp-server`).
-   **Data Source:** "Gong" call transcripts stored in Redshift.
-   **Output:** Structured JSON containing date, participants, and transcript text.

### C. Sub-Agent 2: "The Email Specialist"
-   **Role:** Retrieve email correspondence.
-   **Tooling:** Connected via **MCP** to an Email/Gmail server.
-   **Output:** Structured JSON containing date, sender/receiver, and body text.

### D. Sub-Agent 3: "The Timeline Organizer"
-   **Role:** Data Pre-processing.
-   **Responsibility:** Takes raw lists from the Redshift and Email agents and merges them into a single, chronological timeline.
-   **Method:** Deterministic Python logic (invoked as a tool) to sort events by timestamp.
-   **Goal:** Ensure the Analyzer sees the conversation flow (Email -> Call -> Email) correctly.

### E. Sub-Agent 4: "The Churn Analyzer"
-   **Role:** Insight Generation.
-   **Responsibility:** Reads the chronological timeline. Detects negative sentiment, competitor mentions, pricing pushback, or lack of engagement.
-   **Output:** A Churn Risk Score (0-100) and a qualitative summary.

## 4. Implementation Details

### Redshift MCP Configuration
We will use the official AWS Labs server.
**Configuration (`mcp_config.json`):**
```json
{
  "mcpServers": {
    "awslabs.redshift-mcp-server": {
      "command": "uvx",
      "args": ["awslabs.redshift-mcp-server@latest"],
      "env": {
        "AWS_REGION": "us-east-1",
        "FASTMCP_LOG_LEVEL": "INFO"
      }
    }
  }
}
```

### Python Implementation Concept
We will configure the ADK `ModelClient` to point to AWS Bedrock instead of Vertex AI.

```python
# Pseudo-code for Bedrock integration in ADK
from adk.models import BedrockModelClient

bedrock_client = BedrockModelClient(model_id="anthropic.claude-3-5-sonnet...")

# The Redshift Agent
redshift_agent = LlmAgent(
    model_client=bedrock_client,
    tools=[McpToolset(config=redshift_mcp_config)]
)
```

## 5. Development Roadmap
1.  **Setup:** Initialize new `uv` repo. Install ADK libraries.
2.  **Bedrock Integration:** Configure ADK to use the Bedrock client.
3.  **Redshift Connection:** Configure and test the `redshift-mcp-server` via MCP.
4.  **Agent Construction:** Build the Manager and Sub-agents.
5.  **UI:** Launch the ADK Web UI.
