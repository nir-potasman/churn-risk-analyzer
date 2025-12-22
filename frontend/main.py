"""
Frontend Service - Professional Chatbot UI.
Serves a dark-mode chat interface for the Churn Risk Analyzer.
"""
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import httpx
import os

app = FastAPI(
    title="Stampli Churn Risk Analyzer",
    description="Professional chatbot UI for churn risk analysis",
    version="2.0.0"
)

# Mount static files
app.mount("/static", StaticFiles(directory="frontend/static"), name="static")

# Setup Jinja2 templates
templates = Jinja2Templates(directory="frontend/templates")

# Manager service URL (from environment or default for Docker)
MANAGER_URL = os.getenv("MANAGER_SERVICE_URL", "http://manager-service:8080")


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Serve the main chat interface."""
    return templates.TemplateResponse("chat.html", {"request": request})


@app.post("/api/query")
async def query(request: Request):
    """Proxy query to manager service and return response."""
    body = await request.json()
    user_query = body.get("user_query", "")
    
    if not user_query:
        return {"error": "No query provided"}
    
    try:
        async with httpx.AsyncClient(timeout=300.0) as client:
            response = await client.post(
                f"{MANAGER_URL}/query",
                json={"user_query": user_query}
            )
            response.raise_for_status()
            return response.json()
    except httpx.TimeoutException:
        return {"error": "Request timed out. The analysis is taking too long."}
    except httpx.HTTPStatusError as e:
        return {"error": f"Manager service error: {e.response.status_code}"}
    except Exception as e:
        return {"error": f"Failed to connect to manager service: {str(e)}"}


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy", "service": "frontend"}

