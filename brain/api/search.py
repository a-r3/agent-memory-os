"""Search-focused compatibility helpers over the canonical memory API."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Sequence

from brain.api.memory_api import MemoryAPI


class SearchAPI:
    """Focused search wrapper that preserves centralized retrieval behavior."""

    def __init__(self, memory_api: Optional[MemoryAPI] = None) -> None:
        self.memory_api = memory_api or MemoryAPI()

    def search(
        self,
        *,
        query: str,
        k: int = 10,
        types: Optional[Sequence[str]] = None,
        memory_scope: Optional[Sequence[str]] = None,
        repo_scope: Optional[Sequence[str]] = None,
    ) -> List[Dict[str, Any]]:
        """Perform cross-type search through the canonical memory API."""
        return self.memory_api.search_memory(
            query=query,
            k=k,
            types=types,
            memory_scope=memory_scope,
            repo_scope=repo_scope,
        )
