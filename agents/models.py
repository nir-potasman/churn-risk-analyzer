from pydantic import BaseModel, Field
from typing import List, Literal, Optional

class CallTranscript(BaseModel):
    date: str = Field(description="Date of the call (YYYY-MM-DD)")
    time: str = Field(default="N/A", description="Time of the call (HH:MM:SS) or N/A if not available")
    title: str = Field(description="Title of the call")
    duration: int = Field(description="Duration of the call in seconds")
    company: str = Field(description="Name of the customer company (e.g., Vivo Infusion)")
    stampli_contact: str = Field(description="Name of the Stampli representative/host. If unknown, use 'Stampli Rep'.")
    company_contact: str = Field(description="Name(s) of the company representative(s). If unknown, use 'Unknown'.")
    department: str = Field(default="Unknown", description="Stampli department: CS, SDR, Sales, Support, or Unknown")
    gong_url: str = Field(description="URL to the Gong call")
    transcript: str = Field(description="The full transcript text, combined chronologically. Do NOT include timestamps for every sentence, just the text.")

class CallTranscriptList(BaseModel):
    transcripts: List[CallTranscript] = Field(description="List of retrieved call transcripts")

class RiskSignal(BaseModel):
    category: str = Field(description="Category of the risk (e.g., Competitor, Pricing, Support, Sentiment)")
    description: str = Field(description="Explanation of the signal found in the text")
    severity: str = Field(description="Severity level: Low, Medium, High, Critical")
    weight_impact: int = Field(description="Estimated impact on churn score (e.g., +20)")

class NextStepRecommendation(BaseModel):
    action: str = Field(description="The recommended action")
    rationale: str = Field(description="Why this action is recommended")
    urgency: str = Field(description="Urgency: Low, Medium, High")

class ChurnRiskAssessment(BaseModel):
    churn_score: int = Field(description="Risk score from 0-100 (0=Safe, 100=Churn Imminent)")
    risk_level: str = Field(description="Overall risk level: Low, Medium, High, Critical")
    sentiment_analysis: str = Field(description="Detailed sentiment analysis of the call")
    summary: str = Field(description="Executive summary of the conversation")
    red_flags: List[str] = Field(description="List of critical red flags")
    signals: List[RiskSignal] = Field(description="Detailed breakdown of risk signals")
    recommendations: List[NextStepRecommendation] = Field(description="List of actionable next steps")


# ==================== Manager Agent Models ====================

class ManagerState(BaseModel):
    """State for Manager Agent StateGraph."""
    user_query: str
    company_name: str = ""
    call_id: str = ""  # Direct call ID lookup (takes precedence over company_name)
    intent: Literal["transcript", "analysis"] = "analysis"
    limit: int = 5  # Number of transcripts to retrieve
    transcripts: Optional[CallTranscriptList] = None
    assessment: Optional[ChurnRiskAssessment] = None

    class Config:
        arbitrary_types_allowed = True


class IntentExtraction(BaseModel):
    """Structured output for intent extraction from user query."""
    company_name: str = Field(
        default="",
        description="The company name to analyze. Leave empty if call_id is provided."
    )
    call_id: str = Field(
        default="",
        description="Call ID if user provides one (e.g., '5723497959273374432'). Takes precedence over company_name."
    )
    intent: Literal["transcript", "analysis"] = Field(
        description="Use 'analysis' if user asks for churn risk, analysis, assessment, risk score. "
                    "Use 'transcript' ONLY if user explicitly asks for transcripts, calls, or conversation records."
    )
    limit: int = Field(
        default=0,  # 0 means "use smart default based on intent"
        description="Number of transcripts requested. Extract from phrases like 'last 3 calls', '5 transcripts', 'latest 2'. Use 0 if not explicitly specified."
    )
