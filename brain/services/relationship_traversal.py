"""
Relationship traversal utilities for Agent Memory OS.

This service provides Phase 6 graph-style traversal over the current in-memory
link registry. It depends on ``MemoryAPI`` for all reads so callers can reason
about relationships without bypassing the canonical memory facade.
"""

from __future__ import annotations

from collections import deque
from typing import Any, Dict, List, Optional, Sequence

from brain.api.memory_api import MemoryAPI


class RelationshipTraversalService:
    """
    Traverse typed relationships between memory objects.

    The current implementation performs breadth-first traversal over the in-memory
    link registry and returns normalized node/edge summaries suitable for tests,
    reports, and future retrieval expansion.
    """

    def __init__(self, memory_api: MemoryAPI) -> None:
        self.memory_api = memory_api

    def traverse(
        self,
        *,
        root_id: str,
        depth: int = 1,
        link_types: Optional[Sequence[str]] = None,
    ) -> Dict[str, Any]:
        """
        Traverse links outward from ``root_id`` up to ``depth`` hops.

        The traversal is read-only. It returns normalized nodes and edges so
        later retrieval or reporting layers can consume the results directly.
        """
        if not isinstance(root_id, str) or not root_id.strip():
            raise ValueError("root_id must be a non-empty string")
        if depth < 0:
            raise ValueError("depth must be zero or greater")

        allowed_link_types = {
            item.strip()
            for item in (link_types or [])
            if isinstance(item, str) and item.strip()
        }

        visited = {root_id}
        queue = deque([(root_id, 0)])
        nodes: Dict[str, Dict[str, Any]] = {}
        edges: List[Dict[str, Any]] = []

        while queue:
            current_id, current_depth = queue.popleft()
            current_object = self.memory_api.get_object_by_id(current_id)
            if current_object is None:
                continue

            nodes[current_id] = self.memory_api.normalize_object(current_object)
            if current_depth >= depth:
                continue

            for link in self.memory_api.list_links():
                if allowed_link_types and link.get("link_type") not in allowed_link_types:
                    continue
                if link.get("source_id") == current_id:
                    neighbor_id = link.get("target_id")
                elif link.get("target_id") == current_id:
                    neighbor_id = link.get("source_id")
                else:
                    continue

                edges.append(dict(link))
                if neighbor_id and neighbor_id not in visited:
                    visited.add(neighbor_id)
                    queue.append((neighbor_id, current_depth + 1))

        return {
            "root_id": root_id,
            "depth": depth,
            "nodes": list(nodes.values()),
            "edges": edges,
        }

    def expand_priority_ids(
        self,
        *,
        task: str,
        k: int = 5,
        depth: int = 1,
        types: Optional[Sequence[str]] = None,
        memory_scope: Optional[Sequence[str]] = None,
        repo_scope: Optional[Sequence[str]] = None,
    ) -> List[str]:
        """
        Expand top-ranked search anchors into a related-id priority set.

        This method is useful for context compilation and reporting because it
        turns search anchors into a small related neighborhood of ids that can
        receive downstream prioritization.
        """
        seed_results = self.memory_api.search_memory(
            query=task,
            k=k,
            types=types,
            memory_scope=memory_scope,
            repo_scope=repo_scope,
        )
        priority_ids = {result["id"] for result in seed_results if result.get("id")}
        for result in seed_results:
            object_id = result.get("id")
            if not object_id:
                continue
            traversal = self.traverse(root_id=object_id, depth=depth)
            for node in traversal["nodes"]:
                if node.get("id"):
                    priority_ids.add(node["id"])
        return sorted(priority_ids)
