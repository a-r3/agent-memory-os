"""Background compaction worker scaffold."""

from __future__ import annotations

from typing import Dict, Optional

from apps.writeback.dedupe import DedupeService
from apps.writeback.promotion import PromotionPlanner
from brain.api.memory_api import MemoryAPI


class CompactionWorker:
    """Run non-destructive hygiene and optimization passes."""

    def __init__(self, memory_api: Optional[MemoryAPI] = None) -> None:
        self.memory_api = memory_api or MemoryAPI()
        self.dedupe_service = DedupeService(self.memory_api)
        self.promotion_planner = PromotionPlanner(self.memory_api)

    def run(self) -> Dict[str, object]:
        """Return duplicate and promotion signals for downstream automation."""
        return {
            "dedupe": self.dedupe_service.duplicate_report(),
            "promotion": self.promotion_planner.promotion_report(),
            "tiers": self.memory_api.memory_tier_report(),
        }
