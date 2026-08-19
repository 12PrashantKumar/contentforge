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
GITHUB_TOKEN = require_env("GITHUB_TOKEN")
CONTENTFORGE_DATABASE_URL = require_env("CONTENTFORGE_DATABASE_URL")
REDIS_URL = require_env("REDIS_URL")


# Has a sensible default, so it doesn't need require_env().
GROQ_MODEL = os.getenv(
    "GROQ_MODEL",
    "llama-3.3-70b-versatile",
)