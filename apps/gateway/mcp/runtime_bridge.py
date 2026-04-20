"""Future-phase runtime capability bridge for gateway-side MCP discovery."""

from __future__ import annotations

from typing import Dict

from mcp.tools import MemoryTools


def build_runtime_capability_map(memory_tools: MemoryTools) -> Dict[str, str]:
    """Return a stable runtime-oriented capability map."""
    return {
        "runtime_payload_preview": memory_tools.runtime_payload_preview.__name__,
        "context_optimize": memory_tools.context_optimize.__name__,
        "context_budget_report": memory_tools.context_budget_report.__name__,
        "memory_trust_report": memory_tools.memory_trust_report.__name__,
    }
