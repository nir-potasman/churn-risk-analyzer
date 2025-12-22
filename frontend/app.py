import streamlit as st
import requests
import json
import os
import time

# Configuration
MANAGER_URL = os.getenv("MANAGER_URL", "http://manager-service:8080")

st.set_page_config(page_title="Stampli Churn Analyzer", page_icon="📉", layout="wide")

st.title("📉 Churn Risk Analyzer")
st.markdown("Enter a company name to analyze their latest calls for churn risk.")

# Sidebar for Debugging
with st.sidebar:
    st.header("⚙️ Debug Configuration")
    method_name = st.selectbox(
        "JSON-RPC Method",
        [
            "account_manager.generate", 
            "agent.generate",
            "generate",
            "process",
            "agent.process",
            "invoke",
            "agent.invoke",
            "model.generate"
        ],
        index=0,
        help="Select the JSON-RPC method to try against the Manager Agent."
    )
    
    st.markdown("---")
    st.info(f"Manager URL: `{MANAGER_URL}`")

# Main Input
col1, col2 = st.columns([3, 1])
with col1:
    company_name = st.text_input("Company Name", placeholder="e.g., Vivo Infusion")

with col2:
    st.write("") # Spacer
    st.write("") 
    analyze_btn = st.button("Analyze Risk", type="primary", use_container_width=True)

if analyze_btn:
    if not company_name:
        st.warning("Please enter a company name.")
    else:
        st.markdown("---")
        status_container = st.container()
        
        with status_container:
            with st.spinner(f"Analyzing calls for {company_name}... (This involves real-time DB queries & LLM analysis)"):
                try:
                    # Construct Payload
                    payload = {
                        "jsonrpc": "2.0",
                        "method": method_name,
                        "params": {
                            "input": f"Give me a churn risk analysis for {company_name}"
                        },
                        "id": 1
                    }
                    
                    # Display the request being sent (for debugging)
                    with st.expander("Show Request Payload", expanded=False):
                        st.json(payload)
                    
                    # Call the Manager Agent
                    start_time = time.time()
                    response = requests.post(
                        f"{MANAGER_URL}/", 
                        json=payload,
                        headers={"Content-Type": "application/json"},
                        timeout=300 # 5 minutes timeout for long analysis
                    )
                    elapsed_time = time.time() - start_time
                    
                    if response.status_code == 200:
                        result = response.json()
                        
                        # Check for JSON-RPC Error
                        if "error" in result:
                            st.error(f"❌ JSON-RPC Error: {result['error'].get('message')} (Code: {result['error'].get('code')})")
                            st.json(result)
                        else:
                            st.success(f"✅ Analysis Complete in {elapsed_time:.1f}s")
                            
                            # Display Result
                            # The result structure depends on the agent output, usually result['result']
                            output_data = result.get('result', result)
                            
                            # If output is a string (JSON string), parse it
                            if isinstance(output_data, str):
                                try:
                                    # Sometimes it's wrapped in 'text' or similar
                                    # Try to parse if it looks like JSON
                                    if output_data.strip().startswith("{"):
                                        output_data = json.loads(output_data)
                                except:
                                    pass

                            st.markdown("### Analysis Report")
                            st.json(output_data)
                        
                    else:
                        st.error(f"❌ HTTP Error: {response.status_code}")
                        st.text(response.text)
                        
                except requests.exceptions.ConnectionError:
                    st.error(f"❌ Failed to connect to Manager Service at `{MANAGER_URL}`. Is it running?")
                except Exception as e:
                    st.error(f"❌ Unexpected Error: {e}")

st.markdown("---")
st.caption("Stampli Churn Risk Analyzer | Powered by Google ADK & AWS Redshift")

