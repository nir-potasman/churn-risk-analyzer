"""
Gong Database tools - Fast direct API access.
Uses REST API endpoints for quick data retrieval.
"""
import httpx
import base64
from config import settings

# API endpoints
GONG_QUERY_URL = f"{settings.gong_api_base_url}/query"
GONG_TRANSCRIPTS_URL = f"{settings.gong_api_base_url}/transcripts"

# Common headers
HEADERS = {
    "X-API-Key": settings.gong_api_key,
    "Content-Type": "application/json",
}

# Pre-built SQL templates (no agent reasoning needed)
SQL_TEMPLATES = {
    "latest_calls_for_company": """
        SELECT c.id, c.url, c.title, c.started, c.duration, ca.acc_name
        FROM calls c
        JOIN call_accounts ca ON c.id = ca.call_id
        WHERE LOWER(ca.acc_name) LIKE '%{company}%'
        ORDER BY c.started DESC
        LIMIT {limit}
    """,
    
    "participants_for_calls": """
        SELECT call_id, name, affiliation
        FROM call_parties
        WHERE call_id IN ({call_ids})
        AND name IS NOT NULL AND name != ''
    """,
}


def execute_query(sql: str, limit: int = 100) -> list[dict]:
    """Execute SQL query and return results as list of dicts."""
    response = httpx.post(
        GONG_QUERY_URL,
        headers=HEADERS,
        json={"query": sql, "limit": limit},
        timeout=30.0
    )
    response.raise_for_status()
    data = response.json()
    
    # Handle different response formats
    if isinstance(data, list):
        return data
    elif isinstance(data, dict):
        if 'results' in data:
            return data['results']
        elif 'data' in data:
            return data['data']
        elif 'error' in data:
            raise ValueError(f"Query error: {data['error']}")
    return []


def fetch_transcripts(call_ids: list[str]) -> list[dict]:
    """Fetch full transcripts using dedicated /transcripts endpoint.
    
    Makes SEPARATE requests for each call_id to avoid complex parsing.
    This is cleaner and more reliable than parsing combined responses.
    
    Args:
        call_ids: List of call IDs to fetch transcripts for
        
    Returns:
        List of transcript data dicts with call_id and transcript text
    """
    if not call_ids:
        return []
    
    results = []
    
    # Make separate request for each call_id (cleaner than parsing combined response)
    for call_id in call_ids:
        try:
            response = httpx.post(
                GONG_TRANSCRIPTS_URL,
                headers=HEADERS,
                json={"call_ids": [str(call_id)]},
                timeout=30.0
            )
            response.raise_for_status()
            data = response.json()
            
            # Parse the single transcript from openaiFileResponse
            if isinstance(data, dict) and 'openaiFileResponse' in data:
                files = data['openaiFileResponse']
                if files:
                    content_b64 = files[0].get('content', '')
                    content = base64.b64decode(content_b64).decode('utf-8')
                    results.append({
                        'call_id': str(call_id),
                        'transcript': content,
                    })
            elif isinstance(data, list) and data:
                results.append({
                    'call_id': str(call_id),
                    'transcript': str(data[0]),
                })
                
        except Exception as e:
            print(f"Error fetching transcript for call {call_id}: {e}")
            continue
    
    return results


def get_calls_for_company(company_name: str, limit: int = 5) -> list[dict]:
    """Get latest calls for a company using SQL template.
    
    Args:
        company_name: Company name to search for
        limit: Max number of calls to return
        
    Returns:
        List of call metadata dicts
    """
    sql = SQL_TEMPLATES["latest_calls_for_company"].format(
        company=company_name.lower().replace("'", "''"),  # Escape single quotes
        limit=limit
    )
    return execute_query(sql, limit=limit)


def get_participants_for_calls(call_ids: list[str]) -> dict[str, dict]:
    """Get participants for multiple calls, grouped by call_id.
    
    Args:
        call_ids: List of call IDs
        
    Returns:
        Dict mapping call_id to {"stampli": [...], "customer": [...]}
    """
    if not call_ids:
        return {}
    
    # Format call IDs for SQL IN clause
    ids_str = ", ".join(f"'{cid}'" for cid in call_ids)
    sql = SQL_TEMPLATES["participants_for_calls"].format(call_ids=ids_str)
    
    rows = execute_query(sql, limit=500)  # Allow many participants
    
    # Group by call_id and affiliation
    result = {}
    for row in rows:
        call_id = str(row.get('call_id', ''))
        name = row.get('name', '')
        affiliation = row.get('affiliation', '')
        
        if not call_id or not name:
            continue
            
        if call_id not in result:
            result[call_id] = {"stampli": [], "customer": []}
        
        if affiliation == "Internal":
            result[call_id]["stampli"].append(name)
        else:
            result[call_id]["customer"].append(name)
    
    return result


def get_transcripts_for_company(company_name: str, limit: int = 5) -> list[dict]:
    """Three-step fast retrieval: get call IDs, fetch participants, fetch transcripts.
    
    This is the FAST path - no agent reasoning needed.
    
    Args:
        company_name: Company name to search for
        limit: Max number of calls
        
    Returns:
        List of transcript dicts with call metadata and participants
    """
    # Step 1: Get call metadata
    calls = get_calls_for_company(company_name, limit=limit)
    if not calls:
        return []
    
    call_ids = [str(call.get('id')) for call in calls if call.get('id')]
    
    # Step 2: Get participants for all calls (single query)
    participants = get_participants_for_calls(call_ids)
    
    # Step 3: Fetch transcripts using dedicated endpoint
    transcripts = fetch_transcripts(call_ids)
    
    # Merge call metadata with transcripts and participants
    calls_by_id = {str(c.get('id')): c for c in calls}
    
    result = []
    for t in transcripts:
        call_id = str(t.get('call_id', ''))
        call_meta = calls_by_id.get(call_id, {})
        call_participants = participants.get(call_id, {"stampli": [], "customer": []})
        
        result.append({
            **call_meta,
            'transcript': t.get('transcript', t.get('text', '')),
            'call_id': call_id,
            'stampli_contacts': call_participants["stampli"],
            'customer_contacts': call_participants["customer"],
        })
    
    return result
