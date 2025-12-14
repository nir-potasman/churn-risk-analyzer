from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # AWS Configuration
    aws_region: str = "us-east-1"
    aws_access_key_id: Optional[str] = None
    aws_secret_access_key: Optional[str] = None
    aws_session_token: Optional[str] = None

    # Bedrock Configuration
    # We default to the Claude 3.5 Sonnet ID if not provided in env
    bedrock_model_id: str = "bedrock/anthropic.claude-3-5-sonnet-20240620-v1:0"

    # Redshift Configuration (for future use)
    redshift_host: Optional[str] = None
    redshift_port: int = 5439
    redshift_db: Optional[str] = None
    redshift_user: Optional[str] = None
    redshift_password: Optional[str] = None

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore" 

settings = Settings()
