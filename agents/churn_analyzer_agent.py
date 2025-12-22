"""
Churn Analyzer Agent - LangGraph Implementation.
Analyzes call transcripts to calculate churn risk scores.
"""
from langchain_aws import ChatBedrockConverse
from langchain_core.prompts import ChatPromptTemplate
from agents.models import ChurnRiskAssessment
from agents.prompts import CHURN_ANALYZER_INSTRUCTION
from config import settings

# Initialize LLM with structured output
# Using Claude 4.5 Sonnet (smart model) for analysis
llm = ChatBedrockConverse(
    model="eu.anthropic.claude-sonnet-4-5-20250929-v1:0",
    region_name=settings.aws_region,
    temperature=0,
    max_tokens=4096
)

# Create structured output chain
structured_llm = llm.with_structured_output(ChurnRiskAssessment)

# Build the analysis chain with prompt template
analysis_prompt = ChatPromptTemplate.from_messages([
    ("system", CHURN_ANALYZER_INSTRUCTION),
    ("human", "Analyze the following call transcripts and provide a churn risk assessment:\n\n{transcripts}")
])

# Chain: prompt → structured LLM → ChurnRiskAssessment
analyzer_chain = analysis_prompt | structured_llm

# Usage: assessment = analyzer_chain.invoke({"transcripts": transcript_text})
# Returns: ChurnRiskAssessment Pydantic model directly!
