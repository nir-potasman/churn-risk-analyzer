from pydantic_settings import BaseSettings
from typing import Optional
from dotenv import load_dotenv

# Load .env file into os.environ for boto3/LiteLLM to pick up automatically
load_dotenv()

class Settings(BaseSettings):
    # AWS Configuration
    aws_region: str = "eu-west-1"
    aws_access_key_id: Optional[str] = None
    aws_secret_access_key: Optional[str] = None
    aws_session_token: Optional[str] = None

    # OpenAI - only for testing!
    openai_api_key: Optional[str] = None

    # Bedrock Configuration
    # We default to the Claude 4.5 Sonnet ID if not provided in env
    model_id: str = "bedrock/eu.anthropic.claude-sonnet-4-5-20250929-v1:0"

    # A2A Service URLs (Defaults for Docker Compose)
    transcript_agent_url: str = "http://transcript-service:8001"
    churn_agent_url: str = "http://churn-service:8002"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore" 

settings = Settings()
