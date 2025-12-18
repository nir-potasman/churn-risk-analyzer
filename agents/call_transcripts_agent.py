import os
from google.adk.agents.llm_agent import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools.mcp_tool import McpToolset, StdioConnectionParams
from mcp import StdioServerParameters
from config import settings
from agents.prompts import CALL_TRANSCRIPTS_AGENT_INSTRUCTION

# Prepare environment variables for the MCP server
# We copy the entire environment to preserve PATH (needed for uvx) and IAM credentials
mcp_env = os.environ.copy()
mcp_env.update({
    'AWS_DEFAULT_REGION': settings.aws_region,
    'FASTMCP_LOG_LEVEL': 'INFO'
})

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
    model=LiteLlm(model=settings.fast_model_id),
    description="Retrieves call transcripts from Gong database in Redshift",
    instruction=CALL_TRANSCRIPTS_AGENT_INSTRUCTION,
    tools=[redshift_mcp]
)
