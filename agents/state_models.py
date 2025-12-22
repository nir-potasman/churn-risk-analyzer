"""
State models for LangGraph agents.
Defines TypedDict and Pydantic schemas for inter-agent communication.
"""
from typing import TypedDict, Literal, Optional
from pydantic import BaseModel, Field


class ManagerState(BaseModel):
    """State for Manager Agent StateGraph.
    
    Uses Pydantic BaseModel for runtime validation (per LangGraph docs).
    """
    user_query: str
    company_name: str = ""
    intent: Literal["transcript", "analysis"] = "analysis"
    transcripts: dict = Field(default_factory=dict)
    assessment: dict = Field(default_factory=dict)
    final_output: Optional[dict] = None


class IntentExtraction(BaseModel):
    """Structured output for intent extraction from user query."""
    company_name: str = Field(description="The company name to analyze")
    intent: Literal["transcript", "analysis"] = Field(
        description="'transcript' if user only wants call data, 'analysis' for full churn risk"
    )


class RetrieverState(TypedDict):
    """State for Retriever Agent (used with create_react_agent)."""
    messages: list
    company_name: str


class AnalyzerState(TypedDict):
    """State for Analyzer Agent."""
    transcripts: str

