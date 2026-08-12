import time
from typing import Any

from langchain_groq import ChatGroq

from core.config import GROQ_API_KEY, GROQ_MODEL


# One Groq client for the entire application.
llm = ChatGroq(
    model=GROQ_MODEL,
    api_key=GROQ_API_KEY,
    temperature=0.7,
)


def invoke_llm(
    messages: list[Any],
    max_retries: int = 3,
):
    """
    Central gateway for all LLM calls in ContentForge.

    Every agent that needs an LLM should use this function
    rather than creating its own ChatGroq client.

    Retries are intended for temporary LLM/API failures.
    """

    last_error = None

    for attempt in range(max_retries):
        try:
            return llm.invoke(messages)

        except Exception as error:
            last_error = error

            # No retry after the final attempt.
            if attempt == max_retries - 1:
                raise

            wait_seconds = 2 ** attempt

            print(
                f"LLM call failed: {error}"
            )

            print(
                f"Retrying in {wait_seconds} seconds..."
            )

            time.sleep(wait_seconds)

    # This should technically never be reached.
    raise last_error