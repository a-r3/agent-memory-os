"""Future worker for exporting consolidated operational reports."""

from __future__ import annotations

from typing import Dict, Optional

from brain.api.memory_api import MemoryAPI


class ReportingWorker:
    """Produce a consolidated report for future operational exports."""

    def __init__(self, memory_api: Optional[MemoryAPI] = None) -> None:
        self.memory_api = memory_api or MemoryAPI()

    def run(self) -> Dict[str, object]:
        """Return a read-only operational report bundle."""
        return {
            "health": self.memory_api.memory_health_report(),
            "trust": self.memory_api.trust_report(),
            "tiers": self.memory_api.memory_tier_report(),
            "snapshots": self.memory_api.list_snapshot_files(),
        }
