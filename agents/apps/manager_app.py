from google.adk.a2a.utils.agent_to_a2a import to_a2a
from a2a.types import AgentCard, AgentCapabilities
from agents.manager import manager_agent
from starlette.responses import JSONResponse

# Define the Agent Card metadata
agent_card = AgentCard(
    name="account_manager",
    url="http://manager-service:8080",
    description="The Account Manager for Stampli's Churn Risk Analyzer.",
    version="1.0.0",
    capabilities=AgentCapabilities(),
    skills=[],
    default_input_modes=["text/plain"],
    default_output_modes=["text/plain"],
    supports_authenticated_extended_card=False,
)

# Create the A2A application
a2a_app = to_a2a(
    manager_agent, 
    port=8080, 
    agent_card=agent_card
)

# Add health check endpoint for ECS
a2a_app.add_route("/health", lambda r: JSONResponse({"status": "healthy"}), methods=["GET"])
