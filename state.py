from typing import TypedDict


class AgentState(TypedDict):
    # User's original requirement
    user_request: str

    # Tasks assigned by orchestrator
    frontend_task: str
    backend_task: str

    # Individual agent outputs
    frontend_output: str
    backend_output: str

    # Combined final response
    final_output: str

    # Files created from the generated code
    frontend_file: str
    backend_file: str

    # Context-window tracking
    input_tokens: int
    output_tokens: int
    total_tokens: int
    context_limit: int
    remaining_tokens: int
