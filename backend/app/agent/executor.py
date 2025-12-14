from langchain_core.prompts import ChatPromptTemplate
from app.agent.state import AgentState
from app.agent.utils import get_llm
from app.agent.prompts import EXECUTOR_SYSTEM_PROMPT
from app.tools.redshift import get_query_tool, get_db
from pydantic import BaseModel, Field

class SQLQuery(BaseModel):
    """Result of SQL generation."""
    query: str = Field(description="The executable SQL query for Redshift")

def executor_node(state: AgentState):
    print("--- EXECUTOR NODE ---")
    plan = state["plan"]
    if not plan:
        return {"response": "No plan remaining."}

    current_step = plan[0]
    remaining_plan = plan[1:]
    
    print(f"Executing Step: {current_step}")
    
    # Define executor prompt
    executor_prompt = ChatPromptTemplate.from_messages([
        ("system", EXECUTOR_SYSTEM_PROMPT),
        ("human", "{step}")
    ])
    
    db = get_db()
    
    if db:
        # Bind structured output
        llm = get_llm(structured_output=SQLQuery)
        
        msg = executor_prompt.format_messages(step=current_step)
        
        try:
            structured_response = llm.invoke(msg)
            sql_query = structured_response.query
            print(f"Generated SQL: {sql_query}")
            
            # Execute SQL
            tool = get_query_tool()
            result = tool.run(sql_query)
        except Exception as e:
            result = f"Error generating or executing SQL: {e}"
    else:
        result = "[MOCKED] Database not connected. Simulation: Found 5 records matching criteria."

    print(f"Result: {result}")
    
    return {
        "plan": remaining_plan,
        "past_steps": (state.get("past_steps") or []) + [f"Step: {current_step} -> Result: {result}"]
    }

