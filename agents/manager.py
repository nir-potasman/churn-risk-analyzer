"""
Manager Agent - LangGraph Implementation.
Orchestrates the churn risk analysis workflow with conditional routing.
"""
from typing import Literal
from langchain_aws import ChatBedrockConverse
from langgraph.graph import StateGraph, START, END
import httpx
from config import settings
from agents.models import (
    CallTranscriptList, 
    ChurnRiskAssessment, 
    ManagerState, 
    IntentExtraction
)


# Initialize LLM for intent extraction (uses smart model from settings)
llm = ChatBedrockConverse(
    model=settings.smart_model_id,
    region_name=settings.aws_region,
    temperature=0
)
intent_extractor = llm.with_structured_output(IntentExtraction)


def extract_intent(state: ManagerState) -> dict:
    """Parse user query to extract company name, call_id, intent, and limit."""
    prompt = f"""Analyze this user query and extract the relevant information:

Query: "{state.user_query}"

Extraction Rules:

1. CALL_ID (takes precedence over company_name):
   - If user mentions a specific call ID (long number like 5723497959273374432), extract it
   - Examples: "analyze call 5723497959273374432", "get transcript for call ID 123456789"
   - If call_id is found, leave company_name empty

2. COMPANY_NAME:
   - Extract company name if no call_id is provided
   - Examples: "analyze Vivo Infusion", "churn risk for Alpha Energy"

3. INTENT:
   - "analysis" = user wants churn risk ANALYSIS, risk assessment, churn score
   - "transcript" = user ONLY wants raw call transcripts/recordings, NOT analysis
   - DEFAULT TO "analysis" if query mentions risk, churn, or analysis

4. LIMIT:
   - Extract from phrases like "last 3 calls", "latest 5 transcripts"
   - Return 0 if not explicitly specified

Examples:
- "analyze call 5723497959273374432" → call_id: "5723497959273374432", intent: "analysis"
- "get transcript for call ID 123456789" → call_id: "123456789", intent: "transcript"  
- "churn analysis for Vivo Infusion" → company_name: "Vivo Infusion", intent: "analysis"
- "show me the last 3 calls with Alpha Energy" → company_name: "Alpha Energy", intent: "transcript", limit: 3"""
    
    result = intent_extractor.invoke(prompt)
    
    # Apply smart defaults based on intent
    limit = result.limit
    if limit == 0:
        # For analysis: 2 recent calls is enough (faster LLM processing)
        # For transcripts: 5 is a reasonable default
        # For call_id lookup: always 1
        if result.call_id:
            limit = 1
        else:
            limit = 2 if result.intent == "analysis" else 5
    
    return {
        "company_name": result.company_name,
        "call_id": result.call_id,
        "intent": result.intent,
        "limit": limit
    }


def route_after_retrieve(state: ManagerState) -> Literal["analyze", "format"]:
    """Route based on intent after retrieval."""
    if state.intent == "analysis":
        return "analyze"
    return "format"


def call_retriever(state: ManagerState) -> dict:
    """HTTP call to retriever service."""
    # Build request payload - include call_id if provided
    payload: dict[str, str | int] = {"limit": state.limit}
    if state.call_id:
        payload["call_id"] = state.call_id
    else:
        payload["company_name"] = state.company_name
    
    response = httpx.post(
        f"{settings.transcript_agent_url}/retrieve",
        json=payload,
        timeout=180.0  # 3 minutes for DB queries
    )
    response.raise_for_status()
    # Parse response into proper Pydantic model
    transcripts = CallTranscriptList.model_validate(response.json())
    return {"transcripts": transcripts}


def call_analyzer(state: ManagerState) -> dict:
    """HTTP call to analyzer service."""
    # Use explicit timeout with longer read timeout for LLM analysis
    timeout = httpx.Timeout(timeout=300.0, read=300.0)  # 5 minutes for LLM analysis
    response = httpx.post(
        f"{settings.churn_agent_url}/analyze",
        json={"transcripts": state.transcripts.model_dump() if state.transcripts else {}},
        timeout=timeout
    )
    response.raise_for_status()
    # Parse response into proper Pydantic model
    assessment = ChurnRiskAssessment.model_validate(response.json())
    return {"assessment": assessment}


def format_output(state: ManagerState) -> dict:
    """Format final response based on intent."""
    # State is already properly typed, just return it as-is
    # The FastAPI app will serialize it to JSON
    return {}


# Build graph with Pydantic state (per LangGraph docs)
manager_graph = StateGraph(ManagerState)
manager_graph.add_node("extract_intent", extract_intent)
manager_graph.add_node("retrieve", call_retriever)
manager_graph.add_node("analyze", call_analyzer)
manager_graph.add_node("format", format_output)

# Edges with explicit path mapping (per LangGraph docs)
manager_graph.add_edge(START, "extract_intent")
manager_graph.add_edge("extract_intent", "retrieve")
manager_graph.add_conditional_edges(
    "retrieve",
    route_after_retrieve,
    {"analyze": "analyze", "format": "format"}  # Explicit mapping
)
manager_graph.add_edge("analyze", "format")
manager_graph.add_edge("format", END)

# Compile the graph
manager_agent = manager_graph.compile()

# Usage: result = manager_agent.invoke({"user_query": "analyze Vivo Infusion"})
