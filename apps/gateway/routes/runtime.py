"""Future runtime handoff route helpers."""

from __future__ import annotations

from typing import Any, Dict

from apps.gateway.main import GatewayApp


def runtime_payload_route(gateway: GatewayApp, *, agent: str, task: str, budget_tokens: int) -> Dict[str, Any]:
    """Compile a context pack and derive the canonical runtime payload preview."""
    compiled = gateway.compile_context(agent=agent, task=task, budget_tokens=budget_tokens)
    runtime_payload = gateway.memory_tools.runtime_payload_preview(
        agent=agent,
        task=task,
        context_pack=compiled["context_pack"],
    )
    return {
        "context_pack": compiled["context_pack"],
        "context_diagnostics": compiled["context_diagnostics"],
        "runtime_payload": runtime_payload,
    }
