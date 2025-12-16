from google.adk.agents.llm_agent import Agent  # Explicit import
from agents.manager import manager_agent
from agents.call_transcripts_agent import call_transcripts_agent
from agents.churn_analyzer_agent import churn_analyzer_agent

# Switch between agents for testing:
root_agent = manager_agent  # Main Orchestrator
# root_agent = call_transcripts_agent   # For testing Retrieval individually
# root_agent = churn_analyzer_agent # For testing Logic individually

if __name__ == "__main__":
    pass
