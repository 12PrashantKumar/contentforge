import time
from typing import Any

from langchain_groq import ChatGroq

from core.config import GROQ_API_KEY, GROQ_MODEL


# One Groq client for the entire application.
llm = ChatGroq(
    model=GROQ_MODEL,
    api_key=GROQ_API_KEY,
    temperature=0.7,
     reasoning_effort="none",
)


def invoke_llm(
    messages: list,
    max_retries: int = 3,
    json_mode: bool = False,
):
    """
    Central gateway for all LLM calls.

    json_mode=True forces the model to return a valid JSON object
    (Groq response_format). Use it for calls that parse JSON: writer,
    verifier, synthesis, ranker. Leave it False for prose.
    """
    last_error = None

    # bind JSON response format only when requested
    client = llm.bind(response_format={"type": "json_object"}) if json_mode else llm

    for attempt in range(max_retries):
        try:
            return client.invoke(messages)
        except Exception as error:
            last_error = error
            if attempt == max_retries - 1:
                raise
            wait_seconds = 2 ** attempt
            print(f"LLM call failed: {error}")
            print(f"Retrying in {wait_seconds} seconds...")
            time.sleep(wait_seconds)

    raise last_error