"""
Stdlib-only API gateway scaffold for Agent Memory OS.

The gateway is intentionally lightweight. It does not introduce a web
framework; instead it provides importable handler methods that a future HTTP or
RPC transport can wrap. All memory operations delegate through MCP or the
canonical ``MemoryAPI`` rather than bypassing the established architecture.
"""

from __future__ import annotations

from typing import Any, Dict, Optional, Sequence

from brain.api.memory_api import MemoryAPI
from mcp.tools import MemoryTools


class GatewayApp:
    """Thin gateway facade for context, trust, and health endpoints."""

    def __init__(
        self,
        *,
        memory_api: Optional[MemoryAPI] = None,
        memory_tools: Optional[MemoryTools] = None,
    ) -> None:
        self.memory_api = memory_api or MemoryAPI()
        self.memory_tools = memory_tools or MemoryTools(
            retrieval_backend=self.memory_api.retrieval_backend,
            writeback_backend=self.memory_api.writeback_backend,
        )

    def health(self) -> Dict[str, Any]:
        """Return a compact gateway health payload."""
        return {
            "status": "ok",
            "memory_health": self.memory_tools.memory_health_report(),
            "memory_tiers": self.memory_tools.memory_tier_report(),
        }

    def compile_context(
        self,
        *,
        agent: str,
        task: str,
        budget_tokens: int,
        memory_scope: Optional[Sequence[str]] = None,
        repo_scope: Optional[Sequence[str]] = None,
    ) -> Dict[str, Any]:
        """Compile a context pack and attach budget diagnostics."""
        context_pack = self.memory_tools.context_compile(
            agent=agent,
            task=task,
            budget_tokens=budget_tokens,
            memory_scope=list(memory_scope) if memory_scope else None,
            repo_scope=list(repo_scope) if repo_scope else None,
        )
        return {
            "context_pack": context_pack,
            "context_diagnostics": self.memory_tools.context_budget_report(context_pack),
        }

    def trust_report(self) -> Dict[str, Any]:
        """Expose the current corpus trust report."""
        return self.memory_tools.memory_trust_report()


def create_app() -> GatewayApp:
    """Return a default gateway instance for tests and future transports."""
    return GatewayApp()
