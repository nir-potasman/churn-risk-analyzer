from google.adk.a2a.utils.agent_to_a2a import to_a2a
from a2a.types import AgentCard
from agents.churn_analyzer_agent import churn_analyzer_agent
from starlette.responses import JSONResponse

# Define the Agent Card metadata
agent_card = AgentCard(
    name="churn_risk_analyzer",
    url="http://churn-service:8002",
    description="Analyzes customer call transcripts to calculate churn risk scores and identify red flags.",
    version="1.0.0",
    capabilities={},
    skills=[],
    defaultInputModes=["text/plain"],
    defaultOutputModes=["text/plain"],
    supportsAuthenticatedExtendedCard=False,
)

# Create the A2A application
a2a_app = to_a2a(
    churn_analyzer_agent, 
    port=8002, 
    agent_card=agent_card
)

# Add health check endpoint for ECS
a2a_app.add_route("/health", lambda r: JSONResponse({"status": "healthy"}), methods=["GET"])
