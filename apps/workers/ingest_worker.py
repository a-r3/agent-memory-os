"""Background ingest worker scaffold."""

from __future__ import annotations

from typing import Dict, Optional

from brain.api.memory_api import MemoryAPI


class IngestWorker:
    """Import snapshot/export data into the in-memory corpus."""

    def __init__(self, memory_api: Optional[MemoryAPI] = None) -> None:
        self.memory_api = memory_api or MemoryAPI()

    def run(self, *, snapshot_path: str, merge: bool = True) -> Dict[str, object]:
        """Load a snapshot file through the canonical persistence path."""
        return self.memory_api.import_snapshot(snapshot_path=snapshot_path, merge=merge)
