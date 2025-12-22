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
    """Parse user query to extract company name, intent, and limit."""
    prompt = f"""Analyze this user query and extract the company name, intent, and number of transcripts requested:

Query: "{state.user_query}"

Intent Classification Rules:
- "analysis" = user wants churn risk ANALYSIS, risk assessment, churn score, or any analytical insight
- "transcript" = user ONLY wants raw call transcripts/recordings, NOT analysis

Keywords that indicate "analysis" intent:
- "churn", "risk", "analysis", "analyze", "assessment", "score", "evaluate", "health"

Keywords that indicate "transcript" intent:
- "transcript", "recording", "call log", "conversation", "what was said"

Limit Extraction:
- Look for numbers in phrases like "last 3 calls", "latest 5 transcripts", "2 conversations"
- Return 0 if no specific number is mentioned (we'll apply smart defaults later)

DEFAULT TO "analysis" if the query mentions risk, churn, or analysis in any form."""
    
    result = intent_extractor.invoke(prompt)
    
    # Apply smart defaults based on intent
    limit = result.limit
    if limit == 0:
        # For analysis: 2 recent calls is enough (faster LLM processing)
        # For transcripts: 5 is a reasonable default
        limit = 2 if result.intent == "analysis" else 5
    
    return {"company_name": result.company_name, "intent": result.intent, "limit": limit}


def route_after_retrieve(state: ManagerState) -> Literal["analyze", "format"]:
    """Route based on intent after retrieval."""
    if state.intent == "analysis":
        return "analyze"
    return "format"


def call_retriever(state: ManagerState) -> dict:
    """HTTP call to retriever service."""
    response = httpx.post(
        f"{settings.transcript_agent_url}/retrieve",
        json={"company_name": state.company_name, "limit": state.limit},
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
