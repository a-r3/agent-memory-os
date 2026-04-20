"""Gateway route helpers for context-related actions."""

from __future__ import annotations

from typing import Any, Dict, Optional, Sequence

from apps.gateway.main import GatewayApp


def compile_context_route(
    gateway: GatewayApp,
    *,
    agent: str,
    task: str,
    budget_tokens: int,
    memory_scope: Optional[Sequence[str]] = None,
    repo_scope: Optional[Sequence[str]] = None,
) -> Dict[str, Any]:
    """Route helper that forwards context compilation to the gateway facade."""
    return gateway.compile_context(
        agent=agent,
        task=task,
        budget_tokens=budget_tokens,
        memory_scope=memory_scope,
        repo_scope=repo_scope,
    )
