"""
Debug agent with detailed logging of each step
"""
import sys
import logging
from datetime import datetime

# Set up detailed logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s.%(msecs)03d] %(levelname)s - %(message)s',
    datefmt='%H:%M:%S',
    stream=sys.stdout
)

logger = logging.getLogger(__name__)

# Enable LiteLLM debug logging
import litellm
litellm.set_verbose = True

# Import after logging setup
from agents.agent import root_agent

def main():
    logger.info("="*70)
    logger.info("DEBUGGING CHURN RISK ANALYZER PERFORMANCE")
    logger.info("="*70)
    
    query = "give me a churn risk analysis for vivo infusion"
    logger.info(f"Query: {query}")
    logger.info("")
    
    logger.info("🚀 Starting agent invocation...")
    
    try:
        result = root_agent.invoke(query)
        
        logger.info("")
        logger.info("✅ COMPLETE")
        logger.info("="*70)
        logger.info("RESULT:")
        logger.info("="*70)
        print(result)
        
    except Exception as e:
        logger.error(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

