"""Entity-focused compatibility helpers over the canonical memory API."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Sequence

from brain.api.memory_api import MemoryAPI


class EntitiesAPI:
    """Focused entity wrapper for callers that need normalized entity access."""

    def __init__(self, memory_api: Optional[MemoryAPI] = None) -> None:
        self.memory_api = memory_api or MemoryAPI()

    def list(self, *, include_inactive: bool = False) -> List[Dict[str, Any]]:
        """Return normalized entity objects through the canonical API."""
        return self.memory_api.list_objects(types=["entity"], include_inactive=include_inactive)
