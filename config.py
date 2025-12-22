from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional
from dotenv import load_dotenv

# Load .env file into os.environ for boto3 to pick up automatically
load_dotenv()


class Settings(BaseSettings):
    # AWS Configuration
    aws_region: str = "eu-west-1"
    aws_access_key_id: Optional[str] = None
    aws_secret_access_key: Optional[str] = None
    aws_session_token: Optional[str] = None

    # Bedrock Model IDs (for ChatBedrockConverse - no 'bedrock/' prefix needed)
    # Claude 4.5 Sonnet - Smart model for analysis and orchestration
    smart_model_id: str = Field(
        default="eu.anthropic.claude-sonnet-4-5-20250929-v1:0",
        alias="ANALYZER_MODEL_ID",
    )
    # Claude 4.5 Haiku - Fast model for data retrieval
    fast_model_id: str = Field(
        default="eu.anthropic.claude-haiku-4-5-20251001-v1:0",
        alias="RETRIEVER_MODEL_ID",
    )

    # Gong Database API (fast endpoint - replaces boto3 Redshift)
    gong_api_base_url: str = Field(default="", alias="GONG_API_BASE_URL")
    gong_api_key: str = Field(default="", alias="GONG_API_KEY")

    # Service URLs (Defaults for Docker Compose)
    transcript_agent_url: str = "http://transcript-service:8001"
    churn_agent_url: str = "http://churn-service:8002"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


settings = Settings()
