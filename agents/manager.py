"""
Manager Agent - LangGraph Implementation.
Orchestrates the churn risk analysis workflow with conditional routing.
"""
from typing import Literal
from pydantic import BaseModel, Field
from langchain_aws import ChatBedrockConverse
from langgraph.graph import StateGraph, START, END
import httpx
from config import settings


# State model using Pydantic (enables validation per LangGraph docs)
class ManagerState(BaseModel):
    """State for Manager Agent StateGraph."""
    user_query: str
    company_name: str = ""
    intent: Literal["transcript", "analysis"] = "analysis"
    transcripts: dict = Field(default_factory=dict)
    assessment: dict = Field(default_factory=dict)

    class Config:
        arbitrary_types_allowed = True


# Intent extraction using structured output
class IntentExtraction(BaseModel):
    """Structured output for intent extraction from user query."""
    company_name: str = Field(description="The company name to analyze")
    intent: Literal["transcript", "analysis"] = Field(
        description="'transcript' if user only wants call data, 'analysis' for full churn risk"
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
    prompt = f"""Extract the company name and user intent from this query: "{state.user_query}"

Rules:
- If the user asks for "transcript", "call", "calls", or "conversation" → intent is "transcript"
- If the user asks for "analysis", "churn", "risk", or "assessment" → intent is "analysis"
- Default to "analysis" if unclear
- Extract the company name mentioned in the query"""
    
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
    return {"transcripts": response.json()}


def call_analyzer(state: ManagerState) -> dict:
    """HTTP call to analyzer service."""
    response = httpx.post(
        f"{settings.churn_agent_url}/analyze",
        json={"transcripts": state.transcripts},
        timeout=180.0  # 3 minutes for analysis
    )
    response.raise_for_status()
    return {"assessment": response.json()}


def format_output(state: ManagerState) -> dict:
    """Format final response based on intent."""
    # Return the appropriate output based on what the user asked for
    if state.intent == "transcript":
        return state.model_dump()
    return state.model_dump()


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
