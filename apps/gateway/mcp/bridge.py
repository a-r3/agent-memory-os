"""Bridge helpers between the gateway scaffold and MCP tools."""

from __future__ import annotations

from typing import Dict

from mcp.tools import MemoryTools


def build_mcp_capability_map(memory_tools: MemoryTools) -> Dict[str, str]:
    """Return a stable capability map for gateway-side MCP discovery."""
    return {
        "context_compile": memory_tools.context_compile.__name__,
        "context_optimize": memory_tools.context_optimize.__name__,
        "memory_health_report": memory_tools.memory_health_report.__name__,
        "memory_tier_report": memory_tools.memory_tier_report.__name__,
        "memory_snapshot_export": memory_tools.memory_snapshot_export.__name__,
        "memory_snapshot_import": memory_tools.memory_snapshot_import.__name__,
    }
