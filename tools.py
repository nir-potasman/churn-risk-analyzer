from langchain.tools import tool

@tool
def multiply(x: float, y: float) -> float:
    """Multiply two numbers together."""
    return x * y

@tool  
def add(x: float, y: float) -> float:
    """Add two numbers together."""
    return x + y

def get_tools():
    return [multiply, add]

