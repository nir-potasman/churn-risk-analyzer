"""
Gong Database tools for LangChain agents.
Uses fast REST API endpoint instead of boto3 Redshift Data API.
"""
import httpx
import json
from langchain_core.tools import tool
from config import settings

# Build query URL from base URL
GONG_QUERY_URL = f"{settings.gong_api_base_url}/query"


def _execute_query(sql: str, limit: int = 100) -> str:
    """Internal function to execute query via Gong API."""
    try:
        response = httpx.post(
            GONG_QUERY_URL,
            headers={
                "X-API-Key": settings.gong_api_key,
                "Content-Type": "application/json",
            },
            json={"query": sql, "limit": limit},
            timeout=30.0
        )
        response.raise_for_status()
        
        data = response.json()
        
        # Handle different response formats
        if isinstance(data, list):
            # Response is a list of records
            if not data:
                return "No results found"
            
            # Get column names from first record
            columns = list(data[0].keys()) if data else []
            
            output = f"Columns: {', '.join(columns)}\n"
            output += "-" * 50 + "\n"
            for row in data[:100]:
                output += f"{list(row.values())}\n"
            
            if len(data) > 100:
                output += f"\n... and {len(data) - 100} more rows (truncated)"
            
            return output
            
        elif isinstance(data, dict):
            # Response might be wrapped in a dict with 'results' key
            if 'results' in data:
                return _format_results(data['results'])
            elif 'data' in data:
                return _format_results(data['data'])
            elif 'error' in data:
                return f"Query error: {data['error']}"
            else:
                # Return raw dict as formatted JSON
                return json.dumps(data, indent=2)
        else:
            return f"Unexpected response format: {type(data)}"
            
    except httpx.HTTPStatusError as e:
        return f"HTTP error {e.response.status_code}: {e.response.text}"
    except httpx.RequestError as e:
        return f"Request error: {str(e)}"
    except Exception as e:
        return f"Error executing query: {str(e)}"


def _format_results(results: list) -> str:
    """Format a list of result records."""
    if not results:
        return "No results found"
    
    columns = list(results[0].keys()) if results else []
    
    output = f"Columns: {', '.join(columns)}\n"
    output += "-" * 50 + "\n"
    for row in results[:100]:
        output += f"{list(row.values())}\n"
    
    if len(results) > 100:
        output += f"\n... and {len(results) - 100} more rows (truncated)"
    
    return output


@tool
def list_tables(schema: str = "gong") -> str:
    """List all tables in a database schema.
    
    Args:
        schema: The schema name to list tables from (default: 'gong')
    
    Returns:
        List of table names in the schema
    """
    sql = f"""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = '{schema}'
        ORDER BY table_name
    """
    return _execute_query(sql)


@tool
def execute_redshift_query(sql: str) -> str:
    """Execute a SQL query on the Gong database.
    
    Use this tool to query call transcripts, call metadata, and account information.
    Key tables:
    - gong.calls: Call metadata (id, title, started, duration, url)
    - gong.call_transcripts: Transcript segments (call_id, speaker_id, text, start_time)
    - gong.call_accounts: Company associations (call_id, acc_name)
    - gong.call_parties: Call participants (call_id, name, emailaddress)
    
    IMPORTANT: Always use LIMIT clause. Never join call_transcripts without filtering by call_id first.
    
    Args:
        sql: The SQL query to execute
    
    Returns:
        Query results as formatted string
    """
    return _execute_query(sql)
