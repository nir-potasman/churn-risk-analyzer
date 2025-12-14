import boto3
from langchain_aws import ChatBedrockConverse
from app.config import AWS_REGION, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_SESSION_TOKEN

def get_bedrock_client():
    boto3_kwargs = {
        "region_name": AWS_REGION,
        "aws_access_key_id": AWS_ACCESS_KEY_ID,
        "aws_secret_access_key": AWS_SECRET_ACCESS_KEY,
    }
    if AWS_SESSION_TOKEN:
        boto3_kwargs["aws_session_token"] = AWS_SESSION_TOKEN
    
    return boto3.client("bedrock-runtime", **boto3_kwargs)

def get_llm(structured_output=None):
    llm = ChatBedrockConverse(
        client=get_bedrock_client(),
        model="anthropic.claude-sonnet-4-5-20250929-v1:0",
        temperature=0,
        max_tokens=4096
    )
    if structured_output:
        return llm.with_structured_output(structured_output)
    return llm

