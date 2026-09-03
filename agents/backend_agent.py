import os

from dotenv import load_dotenv
from google import genai

from state import AgentState

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


def backend_agent(state: AgentState):
    task = state["backend_task"]

    prompt = f"""
You are a Backend Development Agent.

Your responsibilities:
- Generate Python backend code
- Build FastAPI endpoints
- Implement business logic
- Work with databases and APIs
- Implement RAG and ChromaDB logic when required
- Return one complete, runnable Python FastAPI application that can be saved
  directly as main.py
- Do not generate frontend HTML or CSS
- Do not provide unnecessary explanations
- Return code only, without Markdown code fences

Backend task:
{task}
"""

    generated_chunks = []

    stream = client.interactions.create(
        model="gemini-3.6-flash",
        input=prompt,
        stream=True
    )

    for event in stream:
        if event.event_type == "step.delta":
            if event.delta.type == "text":
                generated_chunks.append(event.delta.text)

    backend_code = "".join(generated_chunks)

    return {
        "backend_output": backend_code
    }
