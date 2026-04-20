"""Minimal generic client example for Agent Memory OS MCP usage."""

from __future__ import annotations

from mcp.tools import MemoryTools


def run_example() -> dict[str, object]:
    tools = MemoryTools()
    context_pack = tools.context_compile(
        agent="generic",
        task="demonstrate generic client usage",
        budget_tokens=800,
    )
    return {
        "context_pack": context_pack,
        "runtime_payload": tools.runtime_payload_preview("generic", "demonstrate generic client usage", context_pack),
    }


if __name__ == "__main__":
    result = run_example()
    print(result["runtime_payload"]["cache_key"])
