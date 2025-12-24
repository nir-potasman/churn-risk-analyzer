"""
Call Transcripts Retrieval - Fast Direct Access.
No LLM reasoning - uses pre-built SQL templates and /transcripts endpoint.
"""
from agents.models import CallTranscript, CallTranscriptList
from agents.tools.redshift_tools import get_transcripts_for_company, get_transcript_by_call_id


def retrieve_transcripts(
    company_name: str = "",
    call_id: str = "",
    limit: int = 5
) -> CallTranscriptList:
    """Fast transcript retrieval using direct API calls.
    
    Supports two lookup modes:
    1. By call_id (direct lookup, takes precedence)
    2. By company_name (searches for latest calls)
    
    Args:
        company_name: Company name to search for
        call_id: Specific call ID to retrieve (takes precedence over company_name)
        limit: Maximum number of transcripts to return
        
    Returns:
        CallTranscriptList with formatted transcripts
    """
    # Choose retrieval method based on input
    if call_id:
        # Direct lookup by call_id
        raw_transcripts = get_transcript_by_call_id(call_id)
    else:
        # Search by company name
        raw_transcripts = get_transcripts_for_company(company_name, limit=limit)
    
    if not raw_transcripts:
        return CallTranscriptList(transcripts=[])
    
    # Convert to Pydantic models
    transcripts = []
    for t in raw_transcripts:
        try:
            # Parse date from 'started' field (database only stores date, not time)
            started = t.get('started', '')
            if isinstance(started, str) and started:
                date_str = started[:10] if len(started) >= 10 else started
            else:
                date_str = str(started) if started else "Unknown"
            # Time is not available in the database
            time_str = "N/A"
            
            # Extract participants - already separated by affiliation
            stampli_contacts = t.get('stampli_contacts', [])
            customer_contacts = t.get('customer_contacts', [])
            
            stampli_contact = ", ".join(stampli_contacts) if stampli_contacts else "Stampli Rep"
            company_contact = ", ".join(customer_contacts) if customer_contacts else "Unknown"
            
            transcript = CallTranscript(
                date=date_str,
                time=time_str,
                title=t.get('title', 'Untitled Call'),
                duration=int(t.get('duration', 0) or 0),
                company=t.get('acc_name', company_name),
                stampli_contact=stampli_contact,
                company_contact=company_contact,
                department=t.get('department', 'Unknown'),
                gong_url=t.get('url', ''),
                transcript=t.get('transcript', 'No transcript available')
            )
            transcripts.append(transcript)
            
        except Exception as e:
            # Skip malformed records but log the error
            print(f"Error processing transcript: {e}")
            continue
    
    return CallTranscriptList(transcripts=transcripts)
