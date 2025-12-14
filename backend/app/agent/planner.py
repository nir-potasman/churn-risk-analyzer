from langchain_core.prompts import ChatPromptTemplate
from app.agent.state import AgentState
from app.agent.utils import get_llm
from app.agent.prompts import PLANNER_SYSTEM_PROMPT
from app.tools.redshift import get_schema_info
from pydantic import BaseModel, Field
from typing import List

class Plan(BaseModel):
    """The sequence of steps to execute."""
    steps: List[str] = Field(description="List of granular SQL-executable steps")

def planner_node(state: AgentState):
    print("--- PLANNER NODE ---")
    
    # Retrieve dynamic schema from Redshift
    try:
        schema_context = get_schema_info()
    except Exception as e:
        schema_context = f"Error retrieving schema: {str(e)}"
        print(schema_context)
    
    planner_prompt = ChatPromptTemplate.from_messages([
        ("system", PLANNER_SYSTEM_PROMPT),
        ("human", "User Question: {input}\n\nPast Steps taken:\n{past_steps}")
    ])
    
    messages = planner_prompt.format_messages(
        schema=schema_context, 
        input=state["input"], 
        past_steps="\n".join(state["past_steps"]) if state.get("past_steps") else "None"
    )
    
    llm = get_llm(structured_output=Plan)
    response = llm.invoke(messages)
    
    # Response is now a Plan object, access steps directly
    new_plan = response.steps
    
    print(f"Generated Plan: {new_plan}")
    
    return {"plan": new_plan}

