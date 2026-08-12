from langchain_core.messages import HumanMessage

from core.llm import invoke_llm


messages = [
    HumanMessage(
        content="Reply with exactly: ContentForge LLM works."
    )
]


response = invoke_llm(messages)

print("Response:")
print(response.content)