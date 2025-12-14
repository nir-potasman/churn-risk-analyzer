from typing import TypedDict, List, Optional
from langchain_core.messages import BaseMessage

class AgentState(TypedDict):
    input: str
    chat_history: List[BaseMessage]
    plan: List[str]          # The steps remaining
    past_steps: List[str]    # Steps completed with their results
    response: str            # Final answer

