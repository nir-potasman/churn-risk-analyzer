from langchain_aws import ChatBedrockConverse
from langchain.agents import create_agent
from config import BedrockConfig
from tools import get_tools

class BedrockAgent:
    def __init__(self, config: BedrockConfig):
        self.client = config.get_bedrock_client()
        self.llm = ChatBedrockConverse(
            model="anthropic.claude-3-5-sonnet-20240620-v1:0",
            temperature=0.1,
            max_tokens=1000,
            client=self.client,
        )
        self.tools = get_tools()
        self.agent = create_agent(
            model=self.llm, 
            tools=self.tools, 
            system_prompt="You are a helpful math assistant. Use tools to solve math problems."
        )

    def run(self, user_input: str) -> str:
        """Runs the agent with the given user input."""
        result = self.agent.invoke({"messages": [{"role": "user", "content": user_input}]})
        # The result is the final state, which contains the list of messages
        return result["messages"][-1].content

