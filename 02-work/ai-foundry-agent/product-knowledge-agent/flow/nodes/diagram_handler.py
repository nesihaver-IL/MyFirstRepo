"""
Node: diagram_handler
Handles diagram retrieval (from knowledge base) or generation (DALL-E 3).
Only runs if DIAGRAM_REQUEST is in the intents list.
Returns: { diagram_url, diagram_mode, diagram_description }
"""

from promptflow.core import tool
from openai import AzureOpenAI


@tool
def diagram_handler(
    intents: list,
    diagrams: list,
    product_hint: str,
    subsystem_hint: str,
    openai_endpoint: str,
    openai_key: str,
    dalle_deployment: str = "dalle3-diagrams",
    score_threshold: float = 0.3,
) -> dict:
    """
    Strategy:
      1. If DIAGRAM_REQUEST not in intents → return no diagram (null)
      2. If a pre-built diagram matches (score >= threshold) → return its blob URL
      3. Otherwise → generate a colored diagram with DALL-E 3
    """

    if "DIAGRAM_REQUEST" not in intents:
        return {
            "diagram_url":         None,
            "diagram_mode":        None,
            "diagram_description": "",
        }

    # ── MODE 1: Return pre-built colored diagram ──────────────────────────────
    if diagrams:
        best = diagrams[0]
        if best.get("score", 0) >= score_threshold and best.get("diagram_url"):
            return {
                "diagram_url":         best["diagram_url"],
                "diagram_mode":        "retrieved",
                "diagram_description": best.get("description", "Architecture diagram from knowledge base"),
            }

    # ── MODE 2: Generate with DALL-E 3 ───────────────────────────────────────
    product_label   = product_hint   if product_hint   != "unknown" else "the product"
    subsystem_label = subsystem_hint if subsystem_hint != "unknown" else "its main components"

    dalle_prompt = (
        f"Create a professional software architecture diagram for:\n"
        f"Product: {product_label}\n"
        f"Subsystem / Focus: {subsystem_label}\n\n"
        "Diagram requirements:\n"
        "- Style: clean, modern enterprise architecture diagram (similar to Microsoft Azure or AWS diagrams)\n"
        "- Background: white\n"
        "- Use DISTINCT COLORS for each component type:\n"
        "    * Blue (#0078D4) = services and APIs\n"
        "    * Green (#107C10) = databases and data stores\n"
        "    * Orange (#CA5010) = message queues and async components\n"
        "    * Purple (#8764B8) = external systems and third-party integrations\n"
        "    * Gray (#605E5C) = infrastructure (load balancers, gateways)\n"
        "- Draw directional arrows between components showing the data/control flow\n"
        "- Label every component with its name and role\n"
        "- Include a color legend in the bottom-right corner\n"
        f"- Title at the top: \"{product_label} — {subsystem_label} Architecture\"\n"
        "- Do NOT use black and white only\n"
        "- Aspect ratio: landscape (wider than tall)\n"
        "- Include at least 5 distinct labeled components"
    )

    try:
        aoai = AzureOpenAI(
            api_key=openai_key,
            azure_endpoint=openai_endpoint,
            api_version="2024-02-01",
        )

        response = aoai.images.generate(
            model=dalle_deployment,
            prompt=dalle_prompt,
            size="1792x1024",   # landscape — best for architecture diagrams
            quality="hd",
            style="natural",    # "natural" gives more realistic precision than "vivid"
            n=1,
        )

        return {
            "diagram_url":         response.data[0].url,
            "diagram_mode":        "generated",
            "diagram_description": f"AI-generated architecture diagram: {product_label} — {subsystem_label}",
        }

    except Exception as e:
        # Graceful fallback — don't crash the whole flow if image generation fails
        return {
            "diagram_url":         None,
            "diagram_mode":        "failed",
            "diagram_description": f"Diagram generation unavailable: {str(e)}",
        }
