from pydantic import BaseModel, Field
from typing import List, Optional

class CallTranscript(BaseModel):
    date: str = Field(description="Date of the call (YYYY-MM-DD)")
    time: str = Field(description="Time of the call (HH:MM:SS)")
    title: str = Field(description="Title of the call")
    duration: int = Field(description="Duration of the call in seconds")
    company: str = Field(description="Name of the customer company (e.g., Vivo Infusion)")
    stampli_contact: str = Field(description="Name of the Stampli representative/host. If unknown, use 'Stampli Rep'.")
    company_contact: str = Field(description="Name(s) of the company representative(s). If unknown, use 'Unknown'.")
    gong_url: str = Field(description="URL to the Gong call")
    transcript: str = Field(description="The full transcript text, combined chronologically. Do NOT include timestamps for every sentence, just the text.")

class CallTranscriptList(BaseModel):
    transcripts: List[CallTranscript] = Field(description="List of retrieved call transcripts")

