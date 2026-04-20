"""Future generic runtime client example."""

from __future__ import annotations

from mcp.tools import MemoryTools


def run_example() -> dict[str, object]:
    tools = MemoryTools()
    context_pack = tools.context_compile(
        agent="generic",
        task="future runtime client example",
        budget_tokens=900,
    )
    return tools.runtime_payload_preview("generic", "future runtime client example", context_pack)


if __name__ == "__main__":
    payload = run_example()
    print(payload["estimated_tokens"])
