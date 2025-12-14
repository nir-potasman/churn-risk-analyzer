from langgraph.graph import StateGraph, START, END
from app.agent.state import AgentState
from app.agent.planner import planner_node
from app.agent.executor import executor_node
from app.agent.prompts import RESPONSE_GENERATOR_SYSTEM_PROMPT
from app.agent.utils import get_llm
from langchain_core.prompts import ChatPromptTemplate
from langfuse.callback import CallbackHandler
from app.config import LANGFUSE_PUBLIC_KEY, LANGFUSE_SECRET_KEY, LANGFUSE_HOST

def response_generator(state: AgentState):
    print("--- RESPONSE GENERATOR ---")
    
    summary_prompt = ChatPromptTemplate.from_messages([
        ("system", RESPONSE_GENERATOR_SYSTEM_PROMPT),
        ("human", "User Question: {input}\n\nExecution History:\n{past_steps}")
    ])
    
    messages = summary_prompt.format_messages(
        input=state["input"],
        past_steps="\n".join(state["past_steps"]) if state.get("past_steps") else "No steps taken."
    )
    
    llm = get_llm()
    response = llm.invoke(messages)
    return {"response": response.content}

def should_continue(state: AgentState):
    if not state["plan"]:
        return "response_generator" 
    return "executor" 

def create_graph():
    workflow = StateGraph(AgentState)
    
    workflow.add_node("planner", planner_node)
    workflow.add_node("executor", executor_node)
    workflow.add_node("response_generator", response_generator)
    
    workflow.add_edge(START, "planner")
    workflow.add_edge("planner", "executor")
    workflow.add_conditional_edges("executor", should_continue)
    workflow.add_edge("response_generator", END)
    
    return workflow.compile()

def get_langfuse_handler():
    if LANGFUSE_PUBLIC_KEY and LANGFUSE_SECRET_KEY:
        return CallbackHandler(
            public_key=LANGFUSE_PUBLIC_KEY,
            secret_key=LANGFUSE_SECRET_KEY,
            host=LANGFUSE_HOST
        )
    return None

