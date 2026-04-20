"""Dedupe reporting helpers for writeback workflows."""

from __future__ import annotations

from typing import Any, Dict, Optional

from brain.api.memory_api import MemoryAPI


class DedupeService:
    """Expose duplicate candidate reporting through the writeback app layer."""

    def __init__(self, memory_api: Optional[MemoryAPI] = None) -> None:
        self.memory_api = memory_api or MemoryAPI()

    def duplicate_report(self) -> Dict[str, Any]:
        """Return the duplicate section of the current memory health report."""
        report = self.memory_api.memory_health_report()
        return {
            "duplicate_candidate_groups": report["duplicate_candidate_groups"],
            "duplicate_candidates": report["duplicate_candidates"],
        }
