"""
Performance test script to identify bottlenecks in the churn risk analyzer
"""
import requests
import json
import time
from datetime import datetime

def log_with_time(message):
    """Log message with timestamp"""
    timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    print(f"[{timestamp}] {message}")

def test_agent_performance():
    """Send a test request and monitor timing"""
    
    # ADK web server endpoint
    url = "http://localhost:8000/agent/invoke"
    
    # Test query
    query = "give me a churn risk analysis for vivo infusion"
    
    payload = {
        "input": query,
        "agent_name": "account_manager"
    }
    
    log_with_time("🚀 Starting request...")
    log_with_time(f"Query: {query}")
    
    start_time = time.time()
    
    try:
        response = requests.post(
            url,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=300  # 5 minute timeout
        )
        
        end_time = time.time()
        elapsed = end_time - start_time
        
        log_with_time(f"✅ Response received in {elapsed:.2f} seconds")
        
        if response.status_code == 200:
            result = response.json()
            log_with_time(f"Response preview: {str(result)[:200]}...")
            
            # Save full response
            with open("performance_test_result.json", "w") as f:
                json.dump(result, f, indent=2)
            log_with_time("📄 Full response saved to performance_test_result.json")
        else:
            log_with_time(f"❌ Error: Status {response.status_code}")
            log_with_time(f"Response: {response.text}")
            
    except requests.exceptions.Timeout:
        log_with_time("⏱️ Request timed out after 5 minutes")
    except requests.exceptions.ConnectionError:
        log_with_time("❌ Connection error - is the server running?")
    except Exception as e:
        log_with_time(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    log_with_time("="*60)
    log_with_time("Performance Test for Churn Risk Analyzer")
    log_with_time("="*60)
    test_agent_performance()

