from pathlib import Path
import re

from langgraph.graph import END, START, StateGraph

from agents.backend_agent import backend_agent
from agents.frontend_agent import frontend_agent
from orchestrator import orchestrator_agent
from state import AgentState


def combine_outputs(state: AgentState):
    final_output = f"""
================ FRONTEND CODE ================

{state["frontend_output"]}


================ BACKEND CODE =================

{state["backend_output"]}
"""

    return {
        "final_output": final_output
    }


def extract_code(generated_output: str, language: str) -> str:
    """Accept both raw model output and a single fenced code block."""
    fenced_code = re.search(
        rf"```(?:{language})?\s*\n?(.*?)```",
        generated_output,
        re.IGNORECASE | re.DOTALL,
    )
    return (fenced_code.group(1) if fenced_code else generated_output).strip()


def save_generated_files(state: AgentState):
    """Persist the two agents' output as a minimal runnable project."""
    project_directory = Path("generated_project")
    frontend_file = project_directory / "frontend" / "index.html"
    backend_file = project_directory / "backend" / "main.py"

    frontend_file.parent.mkdir(parents=True, exist_ok=True)
    backend_file.parent.mkdir(parents=True, exist_ok=True)

    frontend_file.write_text(
        extract_code(state["frontend_output"], "html"),
        encoding="utf-8",
    )
    backend_file.write_text(
        extract_code(state["backend_output"], "python"),
        encoding="utf-8",
    )

    return {
        "frontend_file": str(frontend_file),
        "backend_file": str(backend_file),
    }


# Create graph
workflow = StateGraph(AgentState)

# Add nodes
workflow.add_node("orchestrator", orchestrator_agent)
workflow.add_node("frontend_agent", frontend_agent)
workflow.add_node("backend_agent", backend_agent)
workflow.add_node("combine_outputs", combine_outputs)
workflow.add_node("save_generated_files", save_generated_files)

# Starting point
workflow.add_edge(START, "orchestrator")

# Run frontend and backend agents after orchestration
workflow.add_edge("orchestrator", "frontend_agent")
workflow.add_edge("orchestrator", "backend_agent")

# Wait for both agents, then combine outputs
workflow.add_edge(
    ["frontend_agent", "backend_agent"],
    "combine_outputs"
)

workflow.add_edge("combine_outputs", "save_generated_files")
workflow.add_edge("save_generated_files", END)

# Compile graph
app = workflow.compile()


def run():
    user_request = input("What do you want to build?\n> ")

    initial_state: AgentState = {
        "user_request": user_request,
        "frontend_task": "",
        "backend_task": "",
        "frontend_output": "",
        "backend_output": "",
        "final_output": "",
        "frontend_file": "",
        "backend_file": "",
        "input_tokens": 0,
        "output_tokens": 0,
        "total_tokens": 0,
        "context_limit": 100000,
        "remaining_tokens": 100000,
    }

    result = app.invoke(initial_state)

    print("\n\nFINAL PROJECT OUTPUT:")
    print(result["final_output"])
    print("\nFiles created:")
    print(f"- Frontend: {result['frontend_file']}")
    print(f"- Backend: {result['backend_file']}")


if __name__ == "__main__":
    run()
