"""
Manager Agent - LangGraph Implementation.
Orchestrates the churn risk analysis workflow with conditional routing.
"""
from typing import Literal, Optional
from pydantic import BaseModel, Field
from langchain_aws import ChatBedrockConverse
from langgraph.graph import StateGraph, START, END
import httpx
from config import settings
from agents.models import CallTranscriptList, ChurnRiskAssessment


# State model using Pydantic with proper type annotations
class ManagerState(BaseModel):
    """State for Manager Agent StateGraph."""
    user_query: str
    company_name: str = ""
    intent: Literal["transcript", "analysis"] = "analysis"
    transcripts: Optional[CallTranscriptList] = None
    assessment: Optional[ChurnRiskAssessment] = None

    class Config:
        arbitrary_types_allowed = True


# Intent extraction using structured output
class IntentExtraction(BaseModel):
    """Structured output for intent extraction from user query."""
    company_name: str = Field(description="The company name to analyze")
    intent: Literal["transcript", "analysis"] = Field(
        description="Use 'analysis' if user asks for churn risk, analysis, assessment, risk score. Use 'transcript' ONLY if user explicitly asks for transcripts, calls, or conversation records."
    )


# Initialize LLM for intent extraction
# Using Claude 4.5 Sonnet (smart model) for intent extraction
llm = ChatBedrockConverse(
    model="eu.anthropic.claude-sonnet-4-5-20250929-v1:0",
    region_name=settings.aws_region,
    temperature=0
)
intent_extractor = llm.with_structured_output(IntentExtraction)


def extract_intent(state: ManagerState) -> dict:
    """Parse user query to extract company name and intent."""
    prompt = f"""Analyze this user query and extract the company name and intent:

Query: "{state.user_query}"

Intent Classification Rules:
- "analysis" = user wants churn risk ANALYSIS, risk assessment, churn score, or any analytical insight
- "transcript" = user ONLY wants raw call transcripts/recordings, NOT analysis

Keywords that indicate "analysis" intent:
- "churn", "risk", "analysis", "analyze", "assessment", "score", "evaluate", "health"

Keywords that indicate "transcript" intent:
- "transcript", "recording", "call log", "conversation", "what was said"

DEFAULT TO "analysis" if the query mentions risk, churn, or analysis in any form."""
    
    result = intent_extractor.invoke(prompt)
    return {"company_name": result.company_name, "intent": result.intent}


def route_after_retrieve(state: ManagerState) -> Literal["analyze", "format"]:
    """Route based on intent after retrieval."""
    if state.intent == "analysis":
        return "analyze"
    return "format"


def call_retriever(state: ManagerState) -> dict:
    """HTTP call to retriever service."""
    response = httpx.post(
        f"{settings.transcript_agent_url}/retrieve",
        json={"company_name": state.company_name},
        timeout=180.0  # 3 minutes for DB queries
    )
    response.raise_for_status()
    # Parse response into proper Pydantic model
    transcripts = CallTranscriptList.model_validate(response.json())
    return {"transcripts": transcripts}


def call_analyzer(state: ManagerState) -> dict:
    """HTTP call to analyzer service."""
    response = httpx.post(
        f"{settings.churn_agent_url}/analyze",
        json={"transcripts": state.transcripts.model_dump() if state.transcripts else {}},
        timeout=180.0  # 3 minutes for analysis
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
