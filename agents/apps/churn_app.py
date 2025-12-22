"""
Churn Analyzer Service - FastAPI Application.
Exposes the analyzer chain via REST endpoints.
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Any
import logging
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Churn Analyzer Service",
    description="Analyzes call transcripts to calculate churn risk scores",
    version="2.0.0"
)


class AnalyzeRequest(BaseModel):
    """Request model for churn analysis."""
    transcripts: Any  # Can be dict or list


@app.post("/analyze")
async def analyze_churn(request: AnalyzeRequest):
    """Analyze call transcripts for churn risk.
    
    Args:
        request: Contains the transcripts to analyze
        
    Returns:
        ChurnRiskAssessment as JSON
    """
    # Import here to avoid circular imports
    from agents.churn_analyzer_agent import analyzer_chain
    
    try:
        logger.info("Analyzing transcripts for churn risk")
        
        # Convert transcripts to string for prompt
        if isinstance(request.transcripts, dict):
            transcript_text = json.dumps(request.transcripts, indent=2)
        elif isinstance(request.transcripts, list):
            transcript_text = json.dumps(request.transcripts, indent=2)
        else:
            transcript_text = str(request.transcripts)
        
        # Chain returns ChurnRiskAssessment Pydantic model directly
        assessment = analyzer_chain.invoke({"transcripts": transcript_text})
        
        logger.info(f"Analysis complete. Churn score: {assessment.churn_score}, Risk level: {assessment.risk_level}")
        
        return assessment.model_dump()  # Convert Pydantic to dict
        
    except Exception as e:
        logger.exception(f"Error analyzing transcripts: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health():
    """Health check endpoint for container orchestration."""
    return {"status": "healthy", "service": "churn-analyzer"}
