import boto3
from langchain_aws import ChatBedrock
from config import settings

def get_bedrock_llm(model_id: str = None) -> ChatBedrock:
    """
    Returns a configured ChatBedrock instance.
    Uses the model_id if provided, otherwise defaults to settings.model_id.
    """
    if model_id is None:
        model_id = settings.model_id
        
    client = boto3.client(
        "bedrock-runtime",
        region_name=settings.aws_region,
        aws_access_key_id=settings.aws_access_key_id,
        aws_secret_access_key=settings.aws_secret_access_key,
        aws_session_token=settings.aws_session_token,
    )
    
    return ChatBedrock(
        client=client,
        model_id=model_id,
        model_kwargs={"temperature": 0.0}
    )

