"""Future generic client example for operational reporting."""

from __future__ import annotations

from mcp.tools import MemoryTools


def run_example() -> dict[str, object]:
    tools = MemoryTools()
    return {
        "health": tools.memory_health_report(),
        "trust": tools.memory_trust_report(),
        "tiers": tools.memory_tier_report(),
    }


if __name__ == "__main__":
    print(run_example()["tiers"]["counts"])
