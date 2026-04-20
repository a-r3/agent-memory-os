"""Merge planning helpers for duplicate durable memory."""

from __future__ import annotations

from typing import Any, Dict, Optional

from brain.api.memory_api import MemoryAPI


class MergePlanner:
    """Generate non-destructive merge plans from duplicate candidates."""

    def __init__(self, memory_api: Optional[MemoryAPI] = None) -> None:
        self.memory_api = memory_api or MemoryAPI()

    def build_merge_plan(self) -> Dict[str, Any]:
        """Return duplicate groups and a recommended canonical survivor."""
        report = self.memory_api.memory_health_report()
        groups = []
        for candidate in report["duplicate_candidates"]:
            ids = list(candidate["ids"])
            groups.append(
                {
                    "signature": candidate["signature"],
                    "keep_id": ids[0] if ids else None,
                    "archive_ids": ids[1:],
                    "count": candidate["count"],
                }
            )
        return {"merge_groups": groups}
