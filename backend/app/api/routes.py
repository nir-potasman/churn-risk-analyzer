from fastapi import APIRouter, HTTPException
from app.api.models import ChatRequest, ChatResponse
from app.agent.graph import create_graph, get_langfuse_handler

router = APIRouter()
graph = create_graph()

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    try:
        initial_state = {
            "input": request.message,
            "chat_history": [],
            "plan": [],
            "past_steps": [],
            "response": ""
        }
        
        config = {}
        callbacks = []
        langfuse_handler = get_langfuse_handler()
        if langfuse_handler:
            callbacks.append(langfuse_handler)
            
        if callbacks:
            config["callbacks"] = callbacks
            
        result = await graph.ainvoke(initial_state, config=config)
        
        return ChatResponse(
            response=result["response"],
            plan=result.get("plan", []),
            steps=result.get("past_steps", [])
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def health_check():
    return {"status": "ok"}

