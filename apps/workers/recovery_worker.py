"""Future recovery worker for snapshot replay and validation."""

from __future__ import annotations

from typing import Dict, Optional

from brain.api.memory_api import MemoryAPI


class RecoveryWorker:
    """Replay a snapshot and return post-import health diagnostics."""

    def __init__(self, memory_api: Optional[MemoryAPI] = None) -> None:
        self.memory_api = memory_api or MemoryAPI()

    def run(self, *, snapshot_path: str, merge: bool = True) -> Dict[str, object]:
        """Import a snapshot and return health and trust diagnostics."""
        import_result = self.memory_api.import_snapshot(snapshot_path=snapshot_path, merge=merge)
        return {
            "import_result": import_result,
            "health": self.memory_api.memory_health_report(),
            "trust": self.memory_api.trust_report(),
        }
