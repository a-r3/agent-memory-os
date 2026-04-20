"""Future planner for cache refresh and stable-context recomputation."""

from __future__ import annotations

from typing import Any, Dict

from brain.api.memory_api import MemoryAPI


class CacheRefreshPlanner:
    """Plan whether a task should reuse or refresh stable prompt sections."""

    def __init__(self, memory_api: MemoryAPI) -> None:
        self.memory_api = memory_api

    def plan(self, *, task: str, agent: str) -> Dict[str, Any]:
        """Return a deterministic cache refresh suggestion."""
        tier_report = self.memory_api.memory_tier_report()
        trust_report = self.memory_api.trust_report(types=["memory_entry", "decision"])
        should_refresh = bool(trust_report["flagged_items"])
        return {
            "agent": agent,
            "task": task,
            "should_refresh_stable_context": should_refresh,
            "hot_object_count": tier_report["counts"]["hot"],
            "reason": "refresh due to flagged trust items" if should_refresh else "stable cache is reusable",
        }
