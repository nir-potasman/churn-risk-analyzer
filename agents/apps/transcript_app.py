from google.adk.a2a.utils.agent_to_a2a import to_a2a
from a2a.types import AgentCard
from agents.call_transcripts_agent import call_transcripts_agent

# Define the Agent Card metadata
agent_card = AgentCard(
    name="call_transcript_retriever",
    url="http://transcript-service:8001",
    description="Retrieves call transcripts from Gong database in Redshift",
    version="1.0.0",
    capabilities={},
    skills=[],
    defaultInputModes=["text/plain"],
    defaultOutputModes=["text/plain"],
    supportsAuthenticatedExtendedCard=False,
)

# Create the A2A application
a2a_app = to_a2a(
    call_transcripts_agent, 
    port=8001, 
    agent_card=agent_card
)
