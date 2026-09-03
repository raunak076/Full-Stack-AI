import json
import os
from dotenv import load_dotenv
from google import genai

from state import AgentState

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


def orchestrator_agent(state: AgentState):
    user_request = state["user_request"]

    prompt = f"""
You are a Software Project Orchestrator.

Divide the user's request into two clear tasks:

1. frontend_task:
   Work involving HTML, CSS, JavaScript and user interface.

2. backend_task:
   Work involving Python, FastAPI, database, APIs and RAG.

Return only valid JSON in this exact format:

{{
    "frontend_task": "frontend work",
    "backend_task": "backend work"
}}

User request:
{user_request}
"""

    response_chunks = []

    stream = client.interactions.create(
        model="gemini-3.6-flash",
        input=prompt,
        stream=True
    )

    for event in stream:
        if event.event_type == "step.delta":
            if event.delta.type == "text":
                response_chunks.append(event.delta.text)

    raw_response = "".join(response_chunks)

    # Extract JSON even if Gemini adds ```json
    start = raw_response.find("{")
    end = raw_response.rfind("}") + 1

    try:
        plan = json.loads(raw_response[start:end])

        frontend_task = plan["frontend_task"]
        backend_task = plan["backend_task"]

    except (json.JSONDecodeError, KeyError):
        # Fallback if Gemini returns invalid JSON
        frontend_task = (
            f"Create the frontend components required for: {user_request}"
        )

        backend_task = (
            f"Create the backend components required for: {user_request}"
        )

    print("\nFrontend Task:")
    print(frontend_task)

    print("\nBackend Task:")
    print(backend_task)

    return {
        "frontend_task": frontend_task,
        "backend_task": backend_task
    }
