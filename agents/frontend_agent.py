import os

from dotenv import load_dotenv
from google import genai

from state import AgentState

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


def frontend_agent(state: AgentState):
    task = state["frontend_task"]

    prompt = f"""
You are a Frontend Development Agent.

Your responsibilities:
- Generate HTML, CSS and JavaScript
- Create responsive and professional UI
- Connect frontend with backend APIs when required
- Return one complete, runnable HTML document. Put CSS inside a <style> tag and
  JavaScript inside a <script> tag so it can be saved directly as index.html.
- Do not generate Python or backend code
- Do not provide unnecessary explanations
- Return code only, without Markdown code fences

Frontend task:
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

    frontend_code = "".join(generated_chunks)

    return {
        "frontend_output": frontend_code
    }
