"""
Call Transcripts Agent - LangGraph Implementation.
Retrieves call transcripts from Gong database in Redshift using boto3.
"""
from langchain_aws import ChatBedrockConverse
from langgraph.prebuilt import create_react_agent
from agents.models import CallTranscriptList
from agents.prompts import CALL_TRANSCRIPTS_AGENT_INSTRUCTION
from agents.tools.redshift_tools import execute_redshift_query, list_tables
from config import settings

# Initialize LLM (uses fast model from settings for data retrieval)
llm = ChatBedrockConverse(
    model=settings.fast_model_id,
    region_name=settings.aws_region,
    temperature=0,
    max_tokens=4096
)

# Create agent with response_format for structured output
# Per LangGraph docs: response_format parameter enforces Pydantic schema
retriever_agent = create_react_agent(
    llm,
    tools=[execute_redshift_query, list_tables],
    prompt=CALL_TRANSCRIPTS_AGENT_INSTRUCTION,
    response_format=CallTranscriptList  # Enforces structured output!
)

# Usage: result = retriever_agent.invoke({"messages": [...]})
# Access structured output: result["structured_response"]
