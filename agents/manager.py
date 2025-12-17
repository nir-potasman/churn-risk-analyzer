import os
from google.adk.agents.llm_agent import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools.agent_tool import AgentTool
from config import settings
from agents.prompts import ACCOUNT_MANAGER_INSTRUCTION
from agents.call_transcripts_agent import call_transcripts_agent
from agents.churn_analyzer_agent import churn_analyzer_agent

# Initialize the model using configuration from settings
llm_model = LiteLlm(model=settings.model_id)


manager_agent = Agent(
    name="account_manager",
    model=llm_model,
    description="The Account Manager for Stampli's Churn Risk Analyzer.",
    instruction=ACCOUNT_MANAGER_INSTRUCTION,
    tools=[
        AgentTool(agent=call_transcripts_agent),
        AgentTool(agent=churn_analyzer_agent)
    ]
)
