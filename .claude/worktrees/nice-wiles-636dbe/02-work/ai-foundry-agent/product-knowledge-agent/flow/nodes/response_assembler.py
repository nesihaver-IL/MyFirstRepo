"""
Node: response_assembler
Combines the structured text answer with the diagram (if any) into the final response.
"""

from promptflow.core import tool


@tool
def response_assembler(
    answer: str,
    diagram_url: str,
    diagram_mode: str,
    diagram_description: str,
) -> str:
    """
    Returns a Markdown string ready to render in Copilot Studio / Teams.
    - If a diagram was retrieved or generated → appends it after the text answer
    - If diagram generation failed → appends a brief note
    - If no diagram was requested → returns the text answer unchanged
    """

    response = answer.strip() if answer else ""

    if diagram_url and diagram_mode in ("retrieved", "generated"):
        source_label = (
            "From knowledge base" if diagram_mode == "retrieved"
            else "Generated for this request"
        )
        response += (
            f"\n\n---\n\n"
            f"## Architecture Diagram\n"
            f"*{source_label}*\n\n"
            f"![Architecture Diagram]({diagram_url})\n\n"
            f"_{diagram_description}_\n"
        )

    elif diagram_mode == "failed":
        response += (
            "\n\n---\n\n"
            "> **Note**: Diagram generation was not available for this request. "
            "Try again or contact the AI team.\n"
        )

    return response
