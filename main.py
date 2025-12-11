import sys
from botocore.exceptions import NoCredentialsError, ClientError
from config import BedrockConfig
from agent import BedrockAgent

def main():
    try:
        config = BedrockConfig()
        agent = BedrockAgent(config)
        response = agent.run("What is (3 * 4) + 5?")
        print(response)
    except NoCredentialsError:
        print("\nError: AWS credentials not found.")
        print("Please ensure you have set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY in your .env file or environment.")
    except ClientError as e:
        print(f"\nAWS Client Error: {e}")
    except Exception as e:
        print(f"\nAn error occurred: {e}")

if __name__ == "__main__":
    main()
