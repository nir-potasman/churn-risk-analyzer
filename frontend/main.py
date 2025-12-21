from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import httpx
import os
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Mount static files
app.mount("/static", StaticFiles(directory="frontend/static"), name="static")

# Templates configuration
templates = Jinja2Templates(directory="frontend/templates")

MANAGER_SERVICE_URL = os.getenv("MANAGER_SERVICE_URL", "http://manager-service:8080")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/analyze", response_class=HTMLResponse)
async def analyze(request: Request, company_name: str = Form(...)):
    # Construct the A2A JSON-RPC payload
    payload = {
        "jsonrpc": "2.0",
        "method": "message/send",
        "params": {
            "message": {
                "messageId": "msg-frontend-req",
                "role": "user",
                "parts": [{"text": f"give me a churn risk analysis for {company_name}"}]
            }
        },
        "id": 1
    }

    try:
        async with httpx.AsyncClient(timeout=300.0) as client:
            logger.info(f"Sending request to {MANAGER_SERVICE_URL} with payload: {payload}")
            response = await client.post(MANAGER_SERVICE_URL, json=payload)
            response.raise_for_status()
            
            rpc_response = response.json()
            # logger.info(f"Received RPC response: {json.dumps(rpc_response, indent=2)}") 
            # (Keeping it clean, uncomment if needed)
            
            if "error" in rpc_response:
                return templates.TemplateResponse("index.html", {
                    "request": request,
                    "error": f"RPC Error: {rpc_response['error']}",
                    "company_name": company_name
                })
            
            # --- PARSING LOGIC UPDATE ---
            # The A2A/ADK structure is nested. 
            # We look for "result" -> "artifacts" -> [0] -> "parts" -> [0] -> "text"
            # OR "result" -> "history" -> (find last message from agent) -> "parts" -> [0] -> "text" (or "data" -> "response" -> "result")
            
            result = rpc_response.get("result", {})
            content_text = None
            
            # Strategy 1: Check artifacts (sometimes final output is here)
            artifacts = result.get("artifacts", [])
            if artifacts and "parts" in artifacts[0]:
                parts = artifacts[0]["parts"]
                if parts and "text" in parts[0]:
                    content_text = parts[0]["text"]
            
            # Strategy 2: Check history for the last message from 'agent'
            if not content_text:
                history = result.get("history", [])
                # Iterate backwards to find the last agent message
                for msg in reversed(history):
                    if msg.get("role") == "agent":
                        # Check parts
                        parts = msg.get("parts", [])
                        for part in parts:
                            # It might be in 'text'
                            if "text" in part:
                                content_text = part["text"]
                                break
                            # It might be in 'data' -> 'response' -> 'result' (Tool use response)
                            if "data" in part and "response" in part["data"]:
                                # If the agent returned the tool result directly as its answer
                                response_data = part["data"]["response"]
                                if "result" in response_data:
                                    content_text = response_data["result"]
                                    break
                        if content_text:
                            break

            if not content_text:
                logger.error("No content text found in artifacts or history")
                return templates.TemplateResponse("index.html", {
                    "request": request, 
                    "error": "Empty response from agent (Parsing failed)",
                    "company_name": company_name,
                    "raw_response": json.dumps(rpc_response, indent=2) 
                })
            
            # Clean up potential markdown formatting
            # The text might be wrapped in ```json ... ``` or just ``` ... ```
            clean_text = content_text.strip()
            if "```json" in clean_text:
                clean_text = clean_text.split("```json")[1].split("```")[0].strip()
            elif "```" in clean_text:
                clean_text = clean_text.split("```")[1].split("```")[0].strip()
            
            try:
                # Try to parse as JSON
                assessment = json.loads(clean_text)
                return templates.TemplateResponse("index.html", {
                    "request": request,
                    "assessment": assessment,
                    "company_name": company_name
                })
            except json.JSONDecodeError:
                # Fallback: It's just text/markdown. 
                # We can try to regex extract fields if we really wanted to, 
                # but for now let's display it as raw response or try to reconstruct the model.
                logger.warning(f"Failed to decode JSON. Content: {clean_text[:100]}...")
                
                return templates.TemplateResponse("index.html", {
                    "request": request,
                    "raw_response": content_text, # Display the full markdown text
                    "company_name": company_name
                })

    except Exception as e:
        logger.exception("Error during analysis")
        return templates.TemplateResponse("index.html", {
            "request": request,
            "error": str(e),
            "company_name": company_name
        })
