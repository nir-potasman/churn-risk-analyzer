from langchain_community.utilities import SQLDatabase
from langchain_community.tools.sql_database.tool import QuerySQLDataBaseTool
from app.config import REDSHIFT_HOST, REDSHIFT_DB, REDSHIFT_USER, REDSHIFT_PASSWORD, REDSHIFT_PORT

def get_db():
    if REDSHIFT_HOST and REDSHIFT_USER and REDSHIFT_PASSWORD and REDSHIFT_DB:
        # Construct connection URI: redshift+psycopg2://user:password@host:port/dbname
        db_uri = f"redshift+psycopg2://{REDSHIFT_USER}:{REDSHIFT_PASSWORD}@{REDSHIFT_HOST}:{REDSHIFT_PORT}/{REDSHIFT_DB}"
        return SQLDatabase.from_uri(db_uri)
    return None

def get_query_tool():
    db = get_db()
    if db:
        return QuerySQLDataBaseTool(db=db)
    return None

def get_schema_info() -> str:
    """
    Retrieves the table names and their schemas from the database.
    Returns a formatted string description of the tables.
    """
    db = get_db()
    if db:
        return db.get_table_info()
    return "Error: Database not connected."

