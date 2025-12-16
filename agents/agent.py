from google.adk.agents.llm_agent import Agent  # Explicit import
from agents.manager import manager_agent
from agents.call_transcripts_agent import call_transcripts_agent

# Switch between agents for testing:
# root_agent = manager_agent  # For testing Manager Agent
root_agent = call_transcripts_agent   # For testing Call Transcripts Agent

if __name__ == "__main__":
    pass
