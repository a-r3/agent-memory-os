"""Scope planning helpers for the compiler app."""

from __future__ import annotations

from typing import Dict, List

from brain.api.memory_api import MemoryAPI


class ScopePlanner:
    """Infer light memory and repo scopes from task language."""

    def __init__(self, memory_api: MemoryAPI) -> None:
        self.memory_api = memory_api

    def plan(self, task: str) -> Dict[str, List[str]]:
        """
        Produce a deterministic scope plan.

        The planner is intentionally simple: it searches the corpus to find the
        most relevant object kinds and identifiers, then turns those into
        allow-lists for the canonical compiler path.
        """
        query = task.strip()
        results = self.memory_api.search_memory(query=query, k=5)

        memory_scope: list[str] = []
        repo_scope: list[str] = []
        for result in results:
            kind = str(result["data"].get("kind") or "").strip()
            if kind and kind not in memory_scope:
                memory_scope.append(kind)
            title = str(result.get("title") or "").strip()
            if title and title not in repo_scope:
                repo_scope.append(title)

        return {
            "memory_scope": memory_scope[:5],
            "repo_scope": repo_scope[:5],
        }
