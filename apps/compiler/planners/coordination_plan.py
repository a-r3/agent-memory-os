"""Future planner for multi-agent coordination over shared memory."""

from __future__ import annotations

from typing import Any, Dict, Sequence

from brain.api.memory_api import MemoryAPI


class CoordinationPlanner:
    """Plan shared context and handoff expectations for multiple agents."""

    def __init__(self, memory_api: MemoryAPI) -> None:
        self.memory_api = memory_api

    def plan(self, *, task: str, agents: Sequence[str]) -> Dict[str, Any]:
        """Return a deterministic coordination plan for the requested agents."""
        shared_context = self.memory_api.compile_context(
            agent="coordination",
            task=task,
            budget_tokens=900,
        )
        return {
            "task": task,
            "agents": list(agents),
            "shared_runtime_payload": self.memory_api.build_runtime_payload(
                agent="coordination",
                task=task,
                context_pack=shared_context,
            ),
            "handoff_required": len(agents) > 1,
        }
