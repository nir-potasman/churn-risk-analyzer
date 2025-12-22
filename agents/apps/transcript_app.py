"""
Transcript Retriever Service - FastAPI Application.
Exposes the retriever agent via REST endpoints.
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Transcript Retriever Service",
    description="Retrieves call transcripts from Gong database in Redshift",
    version="2.0.0"
)


class RetrieveRequest(BaseModel):
    """Request model for transcript retrieval."""
    company_name: str


@app.post("/retrieve")
async def retrieve_transcripts(request: RetrieveRequest):
    """Retrieve call transcripts for a company from Redshift.
    
    Args:
        request: Contains the company_name to search for
        
    Returns:
        CallTranscriptList as JSON
    """
    # Import here to avoid circular imports and ensure proper initialization
    from agents.call_transcripts_agent import retriever_agent
    
    try:
        logger.info(f"Retrieving transcripts for company: {request.company_name}")
        
        # create_react_agent is invoked with messages
        result = retriever_agent.invoke({
            "messages": [
                {"role": "user", "content": f"Retrieve call transcripts for {request.company_name}"}
            ]
        })
        
        # Per LangGraph docs: structured output is in "structured_response" key
        if "structured_response" in result and result["structured_response"]:
            logger.info(f"Successfully retrieved transcripts for {request.company_name}")
            return result["structured_response"].model_dump()
        else:
            # Fallback: try to extract from messages
            logger.warning("No structured_response found, checking messages")
            messages = result.get("messages", [])
            if messages:
                last_message = messages[-1]
                if hasattr(last_message, "content"):
                    return {"transcripts": [], "raw_response": str(last_message.content)}
            
            raise HTTPException(
                status_code=500, 
                detail="No structured response received from agent"
            )
            
    except Exception as e:
        logger.exception(f"Error retrieving transcripts: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health():
    """Health check endpoint for container orchestration."""
    return {"status": "healthy", "service": "transcript-retriever"}
