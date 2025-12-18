from google.adk.agents.llm_agent import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools.agent_tool import AgentTool
from google.adk.agents.remote_a2a_agent import RemoteA2aAgent
from config import settings
from agents.prompts import CHURN_ANALYZER_INSTRUCTION
from agents.models import ChurnRiskAssessment

transcript_agent = RemoteA2aAgent(
    name="call_transcript_retriever",
    description="Retrieves call transcripts from Gong database in Redshift",
    agent_card=f"{settings.transcript_agent_url}/.well-known/agent-card.json"
)

churn_analyzer_agent = Agent(
    name="churn_risk_analyzer",
    model=LiteLlm(model=settings.smart_model_id),
    description="Analyzes customer call transcripts to calculate churn risk scores and identify red flags.",
    instruction=CHURN_ANALYZER_INSTRUCTION,
    tools=[AgentTool(agent=transcript_agent)],
    output_schema=ChurnRiskAssessment,
)

