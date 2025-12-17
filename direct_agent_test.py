"""
Direct agent invocation test with detailed timing
"""
import time
from datetime import datetime
from agents.agent import root_agent

def log_with_time(message):
    """Log message with timestamp"""
    timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    print(f"[{timestamp}] {message}")

def test_agent_directly():
    """Test the agent directly without HTTP"""
    
    query = "give me a churn risk analysis for vivo infusion"
    
    log_with_time("="*70)
    log_with_time("DIRECT AGENT PERFORMANCE TEST")
    log_with_time("="*70)
    log_with_time(f"Query: {query}")
    log_with_time("")
    
    start_time = time.time()
    
    try:
        log_with_time("🚀 Invoking agent...")
        
        # Invoke the agent directly
        result = root_agent.invoke(query)
        
        end_time = time.time()
        elapsed = end_time - start_time
        
        log_with_time(f"✅ Agent completed in {elapsed:.2f} seconds ({elapsed/60:.2f} minutes)")
        log_with_time("")
        log_with_time("="*70)
        log_with_time("RESULT:")
        log_with_time("="*70)
        print(result)
        
        # Save to file
        with open("direct_test_result.txt", "w") as f:
            f.write(f"Query: {query}\n")
            f.write(f"Time: {elapsed:.2f} seconds\n")
            f.write(f"Result:\n{result}\n")
        
        log_with_time("")
        log_with_time("📄 Full result saved to direct_test_result.txt")
        
    except Exception as e:
        end_time = time.time()
        elapsed = end_time - start_time
        log_with_time(f"❌ Error after {elapsed:.2f} seconds: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_agent_directly()

