"""Future archival planning helpers for durable memory hygiene."""

from __future__ import annotations

from typing import Any, Dict, Optional

from brain.api.memory_api import MemoryAPI


class ArchivePlanner:
    """Produce non-destructive archive plans from current health signals."""

    def __init__(self, memory_api: Optional[MemoryAPI] = None) -> None:
        self.memory_api = memory_api or MemoryAPI()

    def build_archive_plan(self) -> Dict[str, Any]:
        """Return duplicate and cold-tier objects that are candidates for archival."""
        health = self.memory_api.memory_health_report()
        tiers = self.memory_api.memory_tier_report()
        return {
            "duplicate_candidates": health["duplicate_candidates"],
            "cold_examples": tiers["examples"]["cold"],
            "cold_count": tiers["counts"]["cold"],
        }
