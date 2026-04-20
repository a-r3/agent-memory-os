"""Background graph sync worker scaffold."""

from __future__ import annotations

from typing import Dict, Optional

from brain.api.memory_api import MemoryAPI
from brain.services.relationship_traversal import RelationshipTraversalService


class GraphSyncWorker:
    """Inspect the current relationship graph and export traversal state."""

    def __init__(self, memory_api: Optional[MemoryAPI] = None) -> None:
        self.memory_api = memory_api or MemoryAPI()
        self.traversal_service = RelationshipTraversalService(self.memory_api)

    def run(self, *, root_id: str, depth: int = 1) -> Dict[str, object]:
        """Return a traversal payload for the requested graph root."""
        return self.traversal_service.traverse(root_id=root_id, depth=depth)
