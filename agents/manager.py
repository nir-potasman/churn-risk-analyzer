import os
from google.adk.agents.llm_agent import Agent
from google.adk.models.lite_llm import LiteLlm
from config import settings
from agents.prompts import ACCOUNT_MANAGER_INSTRUCTION

# Initialize the model using configuration from settings
llm_model = LiteLlm(model=settings.bedrock_model_id)

manager_agent = Agent(
    name="account_manager",
    model=llm_model,
    description="The Account Manager for Stampli's Churn Risk Analyzer.",
    instruction=ACCOUNT_MANAGER_INSTRUCTION,
    tools=[], # Tools will be added later (Redshift, Email agents via A2A)
)

