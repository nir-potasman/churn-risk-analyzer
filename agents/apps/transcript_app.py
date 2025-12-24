"""
Transcript Retriever Service - FastAPI Application.
Fast direct retrieval using SQL templates and /transcripts endpoint.
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Transcript Retriever Service",
    description="Fast transcript retrieval from Gong database",
    version="3.0.0"
)


class RetrieveRequest(BaseModel):
    """Request model for transcript retrieval."""
    company_name: str = ""
    call_id: str = ""  # Direct call ID lookup (takes precedence)
    limit: int = 5


@app.post("/retrieve")
async def retrieve_transcripts_endpoint(request: RetrieveRequest):
    """Retrieve call transcripts - FAST direct retrieval.
    
    Supports two modes:
    1. By call_id (direct lookup, takes precedence)
    2. By company_name (searches for latest calls)
    
    Uses pre-built SQL templates and /transcripts endpoint instead of
    LLM agent reasoning. Much faster (~2-3s vs ~15-30s).
    
    Args:
        request: Contains company_name or call_id, and optional limit
        
    Returns:
        CallTranscriptList as JSON
    """
    # Import here to avoid circular imports
    from agents.call_transcripts_agent import retrieve_transcripts
    
    try:
        if request.call_id:
            logger.info(f"Retrieving transcript for call_id: {request.call_id}")
        else:
            logger.info(f"Retrieving transcripts for company: {request.company_name}")
        
        # Direct function call - no LLM reasoning needed!
        result = retrieve_transcripts(
            company_name=request.company_name,
            call_id=request.call_id,
            limit=request.limit
        )
        
        identifier = request.call_id or request.company_name
        logger.info(f"Successfully retrieved {len(result.transcripts)} transcripts for {identifier}")
        return result.model_dump()
            
    except Exception as e:
        logger.exception(f"Error retrieving transcripts: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health():
    """Health check endpoint for container orchestration."""
    return {"status": "healthy", "service": "transcript-retriever"}
