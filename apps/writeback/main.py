"""
Writeback application scaffold for Agent Memory OS.

This app groups the canonical writeback and hygiene hooks so workers or future
transports can submit session outcomes, inspect duplicate candidates, and
request promotion suggestions without bypassing the memory API.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from apps.writeback.dedupe import DedupeService
from apps.writeback.merge import MergePlanner
from apps.writeback.promotion import PromotionPlanner
from brain.api.memory_api import MemoryAPI


class WritebackApp:
    """Facade for canonical writeback plus Phase 7 hygiene workflows."""

    def __init__(self, memory_api: Optional[MemoryAPI] = None) -> None:
        self.memory_api = memory_api or MemoryAPI()
        self.merge_planner = MergePlanner(self.memory_api)
        self.dedupe_service = DedupeService(self.memory_api)
        self.promotion_planner = PromotionPlanner(self.memory_api)

    def submit_session_delta(self, delta: Dict[str, Any]) -> str:
        """Persist a structured session delta through the canonical API."""
        return self.memory_api.write_session_delta(delta)

    def submit_memory_entry(self, entry: Dict[str, Any]) -> str:
        """Persist a memory entry through the canonical API."""
        return self.memory_api.write_memory_entry(entry)

    def register_decision(self, decision: Dict[str, Any]) -> str:
        """Persist a decision through the canonical API."""
        return self.memory_api.register_decision(decision)
