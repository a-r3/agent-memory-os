"""Future generic client example for multi-agent handoff."""

from __future__ import annotations

from mcp.tools import MemoryTools


def run_example() -> dict[str, object]:
    tools = MemoryTools()
    context_pack = tools.context_compile(
        agent="generic",
        task="future handoff client example",
        budget_tokens=850,
    )
    return {
        "context_pack": context_pack,
        "handoff_template": "storage/docs/sessions/session_handoff.template.json",
    }


if __name__ == "__main__":
    print(run_example()["handoff_template"])
