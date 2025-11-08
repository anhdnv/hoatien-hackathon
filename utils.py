import os
from dotenv import load_dotenv

def load_env_variables():
    """Load environment variables from .env file."""
    load_dotenv()
    
    # Check for required environment variables
    required_vars = [
        "AZURE_OPENAI_API_KEY",
        "AZURE_OPENAI_ENDPOINT",
        "AZURE_OPENAI_API_VERSION",
        "AZURE_OPENAI_DEPLOYMENT",
        "AZURE_OPENAI_EMBEDDING_KEY",
        "AZURE_OPENAI_EMBEDDING_DEPLOYMENT"
    ]
    
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        raise EnvironmentError(
            f"Missing required environment variables: {', '.join(missing_vars)}"
        )
