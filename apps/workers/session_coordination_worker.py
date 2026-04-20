"""Future worker for multi-agent session coordination payloads."""

from __future__ import annotations

from typing import Dict, Optional, Sequence

from apps.compiler.planners.coordination_plan import CoordinationPlanner
from brain.api.memory_api import MemoryAPI


class SessionCoordinationWorker:
    """Build shared coordination payloads for multiple agents."""

    def __init__(self, memory_api: Optional[MemoryAPI] = None) -> None:
        self.memory_api = memory_api or MemoryAPI()
        self.coordination_planner = CoordinationPlanner(self.memory_api)

    def run(self, *, task: str, agents: Sequence[str]) -> Dict[str, object]:
        """Return a coordination plan for the provided agents."""
        return self.coordination_planner.plan(task=task, agents=agents)
