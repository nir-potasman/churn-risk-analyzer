"""
Redshift tools for LangChain agents.
Uses boto3 redshift-data API for direct database access.
"""
import boto3
import time
from langchain_core.tools import tool
from config import settings

# Initialize Redshift Data API client with credentials from settings
client = boto3.client(
    'redshift-data',
    region_name=settings.aws_region,
    aws_access_key_id=settings.aws_access_key_id,
    aws_secret_access_key=settings.aws_secret_access_key,
    aws_session_token=settings.aws_session_token
)

# Constants for Redshift cluster
CLUSTER_ID = "ai"
DATABASE = "gong"


@tool
def list_tables(schema: str = "gong") -> str:
    """List all tables in a Redshift schema.
    
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
    """Execute a SQL query on the Gong database in Redshift.
    
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


def _execute_query(sql: str) -> str:
    """Internal function to execute query and wait for results."""
    try:
        # Execute the statement
        response = client.execute_statement(
            ClusterIdentifier=CLUSTER_ID,
            Database=DATABASE,
            Sql=sql,
        )
        query_id = response['Id']
        
        # Poll for completion (max 120 seconds for longer queries)
        for _ in range(120):
            status = client.describe_statement(Id=query_id)
            if status['Status'] == 'FINISHED':
                break
            elif status['Status'] == 'FAILED':
                error_msg = status.get('Error', 'Unknown error')
                return f"Query failed: {error_msg}"
            elif status['Status'] == 'ABORTED':
                return "Query was aborted"
            time.sleep(1)
        else:
            return "Query timed out after 120 seconds"
        
        # Fetch results
        result = client.get_statement_result(Id=query_id)
        
        # Format results
        columns = [col['name'] for col in result['ColumnMetadata']]
        rows = []
        for record in result['Records']:
            row = []
            for field in record:
                # Handle different field types
                if not field:
                    row.append(None)
                elif 'stringValue' in field:
                    row.append(field['stringValue'])
                elif 'longValue' in field:
                    row.append(field['longValue'])
                elif 'doubleValue' in field:
                    row.append(field['doubleValue'])
                elif 'booleanValue' in field:
                    row.append(field['booleanValue'])
                elif 'isNull' in field and field['isNull']:
                    row.append(None)
                else:
                    # Fallback: get first value
                    row.append(list(field.values())[0] if field else None)
            rows.append(row)
        
        # Return as formatted string
        if not rows:
            return "No results found"
        
        output = f"Columns: {', '.join(columns)}\n"
        output += "-" * 50 + "\n"
        for row in rows[:100]:  # Limit output to 100 rows
            output += f"{row}\n"
        
        if len(rows) > 100:
            output += f"\n... and {len(rows) - 100} more rows (truncated)"
        
        return output
        
    except Exception as e:
        return f"Error executing query: {str(e)}"

