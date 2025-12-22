"""Gong database tools for fast data retrieval."""
from agents.tools.redshift_tools import (
    execute_query,
    fetch_transcripts,
    get_calls_for_company,
    get_transcripts_for_company,
    SQL_TEMPLATES,
)

__all__ = [
    "execute_query",
    "fetch_transcripts", 
    "get_calls_for_company",
    "get_transcripts_for_company",
    "SQL_TEMPLATES",
]
