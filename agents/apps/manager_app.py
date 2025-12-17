from google.adk.a2a.utils.agent_to_a2a import to_a2a
from a2a.types import AgentCard
from agents.manager import manager_agent

# Define the Agent Card metadata
agent_card = AgentCard(
    name="account_manager",
    url="http://manager-service:8080",
    description="The Account Manager for Stampli's Churn Risk Analyzer.",
    version="1.0.0",
    capabilities={},
    skills=[],
    defaultInputModes=["text/plain"],
    defaultOutputModes=["text/plain"],
    supportsAuthenticatedExtendedCard=False,
)

# Create the A2A application
a2a_app = to_a2a(
    manager_agent, 
    port=8080, 
    agent_card=agent_card
)
