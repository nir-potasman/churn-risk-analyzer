import os
import boto3
from dotenv import load_dotenv

class BedrockConfig:
    def __init__(self):
        load_dotenv()
        self.aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
        self.aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
        self.aws_region = os.getenv("AWS_REGION")
        if not self.aws_region:
            self.aws_region = "us-east-1"
        self.aws_session_token = os.getenv("AWS_SESSION_TOKEN")

    def get_bedrock_client(self):
        """Creates and returns a configured boto3 Bedrock client."""
        boto3_kwargs = {
            "region_name": self.aws_region,
        }
        if self.aws_access_key_id:
            boto3_kwargs["aws_access_key_id"] = self.aws_access_key_id
        if self.aws_secret_access_key:
            boto3_kwargs["aws_secret_access_key"] = self.aws_secret_access_key
        if self.aws_session_token:
            boto3_kwargs["aws_session_token"] = self.aws_session_token

        return boto3.client("bedrock-runtime", **boto3_kwargs)

