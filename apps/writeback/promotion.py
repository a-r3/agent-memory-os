"""Promotion planning helpers for repeated episodic content."""

from __future__ import annotations

from typing import Any, Dict, Optional

from brain.api.memory_api import MemoryAPI


class PromotionPlanner:
    """Generate candidate promotion payloads from hygiene signals."""

    def __init__(self, memory_api: Optional[MemoryAPI] = None) -> None:
        self.memory_api = memory_api or MemoryAPI()

    def promotion_report(self) -> Dict[str, Any]:
        """Return promotion candidates from the current memory health report."""
        report = self.memory_api.memory_health_report()
        return {
            "promotion_candidate_groups": report["promotion_candidate_groups"],
            "promotion_candidates": report["promotion_candidates"],
        }
