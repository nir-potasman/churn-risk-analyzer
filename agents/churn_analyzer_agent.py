from google.adk.agents.llm_agent import Agent
from google.adk.models.lite_llm import LiteLlm
from config import settings
from agents.prompts import CHURN_ANALYZER_INSTRUCTION
from agents.models import ChurnRiskAssessment

churn_analyzer_agent = Agent(
    name="churn_risk_analyzer",
    model=LiteLlm(model=settings.model_id),
    description="Analyzes customer call transcripts to calculate churn risk scores and identify red flags.",
    instruction=CHURN_ANALYZER_INSTRUCTION,
    output_schema=ChurnRiskAssessment,
)

