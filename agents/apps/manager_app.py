"""
Manager Service - FastAPI Application.
Exposes the manager agent via REST endpoints.
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Manager Service",
    description="Orchestrates churn risk analysis workflow",
    version="2.0.0"
)


class AnalyzeRequest(BaseModel):
    """Request model for analysis."""
    user_query: str


@app.post("/analyze")
async def handle_query(request: AnalyzeRequest):
    """Process user query and route to appropriate agents.
    
    Args:
        request: Contains the user_query to process
        
    Returns:
        Either CallTranscriptList or ChurnRiskAssessment based on intent
    """
    # Import here to avoid circular imports
    from agents.manager import manager_agent
    
    try:
        logger.info(f"Processing query: {request.user_query}")
        
        # StateGraph is invoked with the state dict
        result = manager_agent.invoke({"user_query": request.user_query})
        
        logger.info(f"Query processed. Intent: {result.get('intent')}, Company: {result.get('company_name')}")
        
        # Return the appropriate output based on intent
        intent = result.get("intent", "analysis")
        
        if intent == "transcript":
            # User asked for transcripts only
            return {
                "intent": "transcript",
                "company_name": result.get("company_name"),
                "transcripts": result.get("transcripts", {})
            }
        else:
            # User asked for full analysis
            return {
                "intent": "analysis",
                "company_name": result.get("company_name"),
                "assessment": result.get("assessment", {})
            }
            
    except Exception as e:
        logger.exception(f"Error processing query: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health():
    """Health check endpoint for container orchestration."""
    return {"status": "healthy", "service": "manager"}
