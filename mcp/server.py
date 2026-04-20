"""Minimal MCP server scaffold for Agent Memory OS."""

from __future__ import annotations

from typing import Any, Dict, Optional

from mcp.prompts import PROMPTS
from mcp.resources import RESOURCES
from mcp.tools import MemoryTools


class MCPServer:
    """
    Thin MCP server facade.

    This is a transport-neutral scaffold that exposes the canonical resources,
    prompts, and tools already defined elsewhere in the repository. A future
    HTTP, stdio, or RPC transport can wrap this object without changing the
    underlying memory contracts.
    """

    def __init__(self, memory_tools: Optional[MemoryTools] = None) -> None:
        self.memory_tools = memory_tools or MemoryTools()

    def describe(self) -> Dict[str, Any]:
        """Return the MCP surface currently available to clients."""
        return {
            "resources": dict(RESOURCES),
            "prompts": dict(PROMPTS),
            "tools": self._tool_names(),
        }

    def _tool_names(self) -> Dict[str, str]:
        return {
            "memory_search": self.memory_tools.memory_search.__name__,
            "memory_write": self.memory_tools.memory_write.__name__,
            "memory_link": self.memory_tools.memory_link.__name__,
            "decision_register": self.memory_tools.decision_register.__name__,
            "session_delta_write": self.memory_tools.session_delta_write.__name__,
            "context_compile": self.memory_tools.context_compile.__name__,
            "context_budget_report": self.memory_tools.context_budget_report.__name__,
            "memory_trust_report": self.memory_tools.memory_trust_report.__name__,
            "memory_health_report": self.memory_tools.memory_health_report.__name__,
            "memory_tier_report": self.memory_tools.memory_tier_report.__name__,
            "runtime_payload_preview": self.memory_tools.runtime_payload_preview.__name__,
            "memory_snapshot_export": self.memory_tools.memory_snapshot_export.__name__,
            "memory_snapshot_import": self.memory_tools.memory_snapshot_import.__name__,
        }
