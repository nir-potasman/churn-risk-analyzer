"""
Churn Analyzer Service - FastAPI Application.
Exposes the analyzer chain via REST endpoints.
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, ValidationError
from typing import Any
import logging
import json
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Churn Analyzer Service",
    description="Analyzes call transcripts to calculate churn risk scores",
    version="2.0.0"
)

# Max retries for LLM structured output failures
MAX_RETRIES = 3


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
    from agents.models import ChurnRiskAssessment
    
    logger.info("Analyzing transcripts for churn risk")
    
    # Convert transcripts to string for prompt
    if isinstance(request.transcripts, dict):
        transcript_text = json.dumps(request.transcripts, indent=2)
    elif isinstance(request.transcripts, list):
        transcript_text = json.dumps(request.transcripts, indent=2)
    else:
        transcript_text = str(request.transcripts)
    
    # Retry loop for LLM structured output failures
    last_error = None
    for attempt in range(MAX_RETRIES):
        try:
            # Chain returns ChurnRiskAssessment Pydantic model directly
            assessment = analyzer_chain.invoke({"transcripts": transcript_text})
            
            logger.info(f"Analysis complete. Churn score: {assessment.churn_score}, Risk level: {assessment.risk_level}")
            
            return assessment.model_dump()  # Convert Pydantic to dict
            
        except ValidationError as e:
            last_error = e
            logger.warning(f"LLM output validation failed (attempt {attempt + 1}/{MAX_RETRIES}): {e}")
            if attempt < MAX_RETRIES - 1:
                time.sleep(1)  # Brief pause before retry
                continue
            
        except Exception as e:
            last_error = e
            logger.warning(f"Error analyzing transcripts (attempt {attempt + 1}/{MAX_RETRIES}): {e}")
            if attempt < MAX_RETRIES - 1:
                time.sleep(1)
                continue
    
    # All retries failed - return a fallback response instead of crashing
    logger.error(f"All {MAX_RETRIES} attempts failed. Returning fallback assessment. Last error: {last_error}")
    
    # Return a fallback "unable to analyze" response
    fallback = {
        "churn_score": 50,
        "risk_level": "Medium",
        "sentiment_analysis": "Unable to complete analysis due to processing error. Manual review recommended.",
        "summary": "Analysis could not be completed automatically. Please review the transcript manually.",
        "red_flags": ["Automated analysis failed - manual review required"],
        "signals": [{
            "category": "Processing Error",
            "description": "LLM structured output parsing failed after multiple retries",
            "severity": "Medium",
            "weight_impact": 0
        }],
        "recommendations": [{
            "action": "Manually review this transcript",
            "rationale": "Automated churn analysis encountered technical difficulties",
            "urgency": "Medium"
        }]
    }
    return fallback


@app.get("/health")
async def health():
    """Health check endpoint for container orchestration."""
    return {"status": "healthy", "service": "churn-analyzer"}
