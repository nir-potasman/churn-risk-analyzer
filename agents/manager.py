import os
from google.adk.agents.llm_agent import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools.agent_tool import AgentTool
from google.adk.agents.remote_a2a_agent import RemoteA2aAgent
from config import settings
from agents.prompts import ACCOUNT_MANAGER_INSTRUCTION

# Initialize the model using configuration from settings
llm_model = LiteLlm(model=settings.smart_model_id)

# Define Remote Agents via A2A
# These point to the separate microservices running in Docker/ECS
# Note: The agent card is served at the root of the service, so we point directly to /.well-known/agent-card.json
churn_agent = RemoteA2aAgent(
    name="churn_risk_analyzer",
    description="Analyzes customer call transcripts to calculate churn risk scores and identify red flags.",
    agent_card=f"{settings.churn_agent_url}/.well-known/agent-card.json"
)

manager_agent = Agent(
    name="account_manager",
    model=llm_model,
    description="The Account Manager for Stampli's Churn Risk Analyzer.",
    instruction=ACCOUNT_MANAGER_INSTRUCTION,
    tools=[
        AgentTool(agent=churn_agent)
    ]
)
