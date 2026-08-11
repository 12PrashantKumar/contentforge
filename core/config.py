import os
from dotenv import load_dotenv

# Load variables from .env
load_dotenv()


def require_env(name: str) -> str:
    """
    Get a required environment variable.
    Stop the application immediately if it is missing.
    """
    value = os.getenv(name)

    if not value:
        raise RuntimeError(
            f"Missing required environment variable: {name}"
        )

    return value


# Required API keys
GROQ_API_KEY = require_env("GROQ_API_KEY")
TAVILY_API_KEY = require_env("TAVILY_API_KEY")