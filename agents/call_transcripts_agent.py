import os
from google.adk.agents.llm_agent import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools.mcp_tool import McpToolset, StdioConnectionParams
from mcp import StdioServerParameters
from config import settings
from agents.prompts import CALL_TRANSCRIPTS_AGENT_INSTRUCTION

# Prepare environment variables for the MCP server
mcp_env = {
    'AWS_DEFAULT_REGION': settings.aws_region,
    'FASTMCP_LOG_LEVEL': 'INFO'
}

# Pass AWS credentials explicitly if they exist in the environment
# This ensures it works in Docker where AWS_PROFILE might not be configured
for key in ["AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY", "AWS_SESSION_TOKEN", "AWS_PROFILE"]:
    if val := os.getenv(key):
        mcp_env[key] = val

# MCP connection to Redshift
redshift_mcp = McpToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command='uvx',
            args=['awslabs.redshift-mcp-server@latest'],
            env=mcp_env
        )
    ),
    # ONLY READ ONLY TOOLS - AS DISCUSSED WITH GIDO
    tool_filter=[
        'list_clusters',
        'list_databases', 
        'list_schemas',
        'list_tables',
        'list_columns',
        'execute_query'
    ]
)

call_transcripts_agent = Agent(
    name="call_transcript_retriever",
    model=LiteLlm(model=settings.model_id),
    description="Retrieves call transcripts from Gong database in Redshift",
    instruction=CALL_TRANSCRIPTS_AGENT_INSTRUCTION,
    tools=[redshift_mcp]
)
