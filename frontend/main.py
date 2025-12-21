from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import httpx
import os
import json
import logging
import re

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Mount static files
app.mount("/static", StaticFiles(directory="frontend/static"), name="static")

# Templates configuration
templates = Jinja2Templates(directory="frontend/templates")

MANAGER_SERVICE_URL = os.getenv("MANAGER_SERVICE_URL", "http://manager-service:8080")

def strip_markdown(text: str) -> str:
    """Remove markdown formatting from text."""
    # Remove bold/italic markers
    text = re.sub(r'\*\*\*(.+?)\*\*\*', r'\1', text)  # Bold italic
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)      # Bold
    text = re.sub(r'\*(.+?)\*', r'\1', text)          # Italic
    text = re.sub(r'__(.+?)__', r'\1', text)          # Bold alt
    text = re.sub(r'_(.+?)_', r'\1', text)            # Italic alt
    # Remove emoji and extra symbols
    text = re.sub(r'[🔴🟡🟢⚠️📊🚩💰]', '', text)
    # Clean up extra spaces
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def parse_markdown_to_assessment(text: str) -> dict:
    """Fallback parser for when the model returns Markdown instead of JSON."""
    assessment = {
        "churn_score": 0,
        "risk_level": "Unknown",
        "summary": "",
        "sentiment_analysis": "",
        "red_flags": [],
        "signals": [],
        "recommendations": []
    }
    
    try:
        # Log the raw text for debugging
        logger.info(f"Parsing markdown text (first 500 chars): {text[:500]}")
        
        # Extract Score and Risk Level - Handle formats like "75/100" or "Score: 75"
        score_match = re.search(r"(?:Score:?\s*|risk\s*\(?)(\d+)(?:/100|\))", text, re.IGNORECASE)
        if score_match:
            assessment["churn_score"] = int(score_match.group(1))
        
        # Extract risk level
        risk_match = re.search(r"\b(Critical|High|Medium|Low)\s+(?:churn\s+)?risk\b", text, re.IGNORECASE)
        if risk_match:
            assessment["risk_level"] = risk_match.group(1).title()
        elif assessment["churn_score"] > 80:
            assessment["risk_level"] = "Critical"
        elif assessment["churn_score"] > 60:
            assessment["risk_level"] = "High"
        elif assessment["churn_score"] > 40:
            assessment["risk_level"] = "Medium"
        else:
            assessment["risk_level"] = "Low"

        # Extract Summary (first major paragraph or Executive Summary section)
        summary_match = re.search(r"(?:Executive\s+Summary|Summary)\s*[:\n*]+\s*([\s\S]*?)(?=\n##|\n###|\*\*Key Issues|\*\*Sentiment|---)", text, re.IGNORECASE)
        if summary_match:
            summary = summary_match.group(1).strip()
            # Clean up the summary
            summary = strip_markdown(summary)
            # Take first 3 sentences or 500 chars
            sentences = re.split(r'(?<=[.!?])\s+', summary)
            assessment["summary"] = ' '.join(sentences[:3]) if len(sentences) > 1 else summary[:500]
        else:
            # Fallback: extract first substantial paragraph
            paragraphs = [p.strip() for p in text.split('\n\n') if len(p.strip()) > 100]
            if paragraphs:
                assessment["summary"] = strip_markdown(paragraphs[0][:500])

        # Extract Sentiment
        sentiment_match = re.search(r"(?:Sentiment\s+Analysis|Sentiment)\s*[:\n*]+\s*([\s\S]*?)(?=\n##|\n###|---)", text, re.IGNORECASE)
        if sentiment_match:
            sentiment = sentiment_match.group(1).strip()
            assessment["sentiment_analysis"] = strip_markdown(sentiment)

        # Extract Red Flags - improved parsing for numbered lists
        flags_section = re.search(r"(?:Critical\s+)?Red\s+Flags?\s*[🚩]*\s*\n+([\s\S]*?)(?=\n###|\n##|$)", text, re.IGNORECASE)
        if flags_section:
            flags_text = flags_section.group(1)
            logger.info(f"Found red flags section (first 300 chars): {flags_text[:300]}")
            
            # Split by lines and look for numbered/bulleted items
            lines = flags_text.split('\n')
            current_flag = []
            
            for line in lines:
                line = line.strip()
                # Check if this is a new flag item (starts with number or bullet)
                if re.match(r'^(?:\d+\.|\-|\*|•)\s+', line):
                    # Save previous flag if exists
                    if current_flag:
                        flag_text = ' '.join(current_flag)
                        cleaned = strip_markdown(flag_text)
                        if len(cleaned) > 10:
                            assessment["red_flags"].append(cleaned)
                    # Start new flag (remove the number/bullet)
                    current_flag = [re.sub(r'^(?:\d+\.|\-|\*|•)\s+', '', line)]
                elif line and not line.startswith('#'):
                    # Continuation of current flag
                    current_flag.append(line)
                elif line.startswith('###'):
                    # Hit next section
                    break
            
            # Don't forget the last flag
            if current_flag:
                flag_text = ' '.join(current_flag)
                cleaned = strip_markdown(flag_text)
                if len(cleaned) > 10:
                    assessment["red_flags"].append(cleaned)

        logger.info(f"Extracted {len(assessment['red_flags'])} red flags")

        # Extract Risk Signals - parse table format
        signals_section = re.search(r"(?:Churn\s+)?Risk\s+Signals?\s*[:\n]*\s*\|.*?\|.*?\|.*?\|([\s\S]*?)(?=\n###|\n##|\n---|\n\*\*|$)", text, re.IGNORECASE)
        if signals_section:
            signals_text = signals_section.group(1)
            logger.info(f"Found signals section (first 300 chars): {signals_text[:300]}")
            
            # Parse table rows
            lines = [l.strip() for l in signals_text.split('\n') if '|' in l and not re.match(r'^\|[\s\-:]+\|', l)]
            
            for line in lines:
                # Split by | and clean
                parts = [p.strip() for p in line.split('|') if p.strip()]
                if len(parts) >= 4:
                    category = strip_markdown(parts[0])
                    description = strip_markdown(parts[1])
                    severity = strip_markdown(parts[2])
                    weight_str = strip_markdown(parts[3])
                    
                    # Extract numeric weight
                    weight_match = re.search(r'(\d+)', weight_str)
                    weight = int(weight_match.group(1)) if weight_match else 0
                    
                    if category and description:
                        assessment["signals"].append({
                            "category": category,
                            "description": description,
                            "severity": severity,
                            "weight_impact": weight
                        })
        
        logger.info(f"Extracted {len(assessment['signals'])} signals")

        # Extract Recommendations/Action Plan - improved
        recs_section = re.search(r"(?:Immediate\s+)?Action\s+Plan\s*[🎯]*\s*\n+([\s\S]*?)(?=\n##|###\s+Bottom\s+Line|$)", text, re.IGNORECASE)
        if recs_section:
            recs_text = recs_section.group(1)
            logger.info(f"Found recommendations section (first 300 chars): {recs_text[:300]}")
            
            # Find all action items by looking for #### headers or **bold** items followed by bullet points
            # Pattern: #### **URGENCY - timeframe** followed by **Action Title**
            action_pattern = r'####\s+\*\*(CRITICAL|HIGH|MEDIUM|LOW).*?\*\*\s*\n\s*\*\*(.*?)\*\*\s*\n([\s\S]*?)(?=####|\n\n###|$)'
            action_matches = re.findall(action_pattern, recs_text, re.IGNORECASE)
            
            for urgency_raw, action_title, action_body in action_matches:
                urgency = urgency_raw.title()
                action = strip_markdown(action_title)
                
                # Extract rationale from the body
                rationale_match = re.search(r'\*\*Rationale:?\*\*\s*(.*?)(?=\n\n|$)', action_body, re.IGNORECASE | re.DOTALL)
                if rationale_match:
                    rationale = strip_markdown(rationale_match.group(1))
                else:
                    # Use first bullet points as rationale
                    bullets = re.findall(r'^\s*[-*]\s+(.*?)$', action_body, re.MULTILINE)
                    rationale = ' '.join([strip_markdown(b) for b in bullets[:2]]) if bullets else "See action plan"
                
                assessment["recommendations"].append({
                    "action": action[:200],
                    "urgency": urgency,
                    "rationale": rationale[:300]
                })
        
        logger.info(f"Extracted {len(assessment['recommendations'])} recommendations")

        # If we still don't have recommendations, try a simpler approach
        if not assessment["recommendations"]:
            # Look for numbered action items
            action_items = re.findall(r'\d+\.\s+\*\*(.*?)\*\*', text)
            for i, item in enumerate(action_items[:5]):
                assessment["recommendations"].append({
                    "action": strip_markdown(item),
                    "urgency": "High" if i == 0 else "Medium",
                    "rationale": "Extracted from action plan"
                })

        logger.info(f"Final parsed assessment: Score={assessment['churn_score']}, Risk={assessment['risk_level']}, Red Flags={len(assessment['red_flags'])}, Signals={len(assessment['signals'])}, Recommendations={len(assessment['recommendations'])}")

    except Exception as e:
        logger.exception(f"Markdown parsing failed: {e}")
    
    return assessment

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
            
            if "error" in rpc_response:
                return templates.TemplateResponse("index.html", {
                    "request": request,
                    "error": f"RPC Error: {rpc_response['error']}",
                    "company_name": company_name
                })
            
            # --- PARSING LOGIC UPDATE ---
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
                for msg in reversed(history):
                    if msg.get("role") == "agent":
                        parts = msg.get("parts", [])
                        for part in parts:
                            if "text" in part:
                                content_text = part["text"]
                                break
                            if "data" in part and "response" in part["data"]:
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
            clean_text = content_text.strip()
            if "```json" in clean_text:
                clean_text = clean_text.split("```json")[1].split("```")[0].strip()
            elif "```" in clean_text:
                # If it's just wrapped in ``` without json, it might still be JSON
                extracted = clean_text.split("```")[1].split("```")[0].strip()
                # Only use extracted if it looks like JSON
                if extracted.startswith('{'):
                    clean_text = extracted
            
            try:
                # Try to parse as JSON
                assessment = json.loads(clean_text)
                logger.info("Successfully parsed JSON response")
                return templates.TemplateResponse("index.html", {
                    "request": request,
                    "assessment": assessment,
                    "company_name": company_name
                })
            except json.JSONDecodeError:
                # Fallback: Parse the Markdown text manually
                logger.warning(f"Failed to decode JSON. Attempting Markdown fallback.")
                assessment = parse_markdown_to_assessment(clean_text)
                
                return templates.TemplateResponse("index.html", {
                    "request": request,
                    "assessment": assessment,
                    "company_name": company_name
                })

    except Exception as e:
        logger.exception("Error during analysis")
        return templates.TemplateResponse("index.html", {
            "request": request,
            "error": str(e),
            "company_name": company_name
        })
