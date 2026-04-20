"""
Linking utilities for Agent Memory OS.

This service centralizes read-only link operations that are useful for
retrieval, traversal, and hygiene checks.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Sequence, TYPE_CHECKING

if TYPE_CHECKING:
    from brain.services.retrieval import MemoryRetrievalBackend


class LinkingService:
    """Read helpers and integrity checks for the in-memory link registry."""

    def __init__(self, retrieval_backend: MemoryRetrievalBackend) -> None:
        self.retrieval_backend = retrieval_backend

    def neighbors(
        self,
        object_id: str,
        *,
        link_types: Optional[Sequence[str]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Return normalized neighbor records for the given object id.

        Each neighbor record includes the neighbor id, neighbor object, and the
        link record that connects them.
        """
        allowed_link_types = {
            value.strip()
            for value in (link_types or [])
            if isinstance(value, str) and value.strip()
        }
        neighbors: List[Dict[str, Any]] = []
        for link in self.retrieval_backend.get_links_for_id(object_id):
            if allowed_link_types and link.get("link_type") not in allowed_link_types:
                continue
            if link.get("source_id") == object_id:
                neighbor_id = link.get("target_id")
            else:
                neighbor_id = link.get("source_id")
            neighbor = self.retrieval_backend.get_object_by_id(str(neighbor_id))
            neighbors.append(
                {
                    "neighbor_id": neighbor_id,
                    "neighbor": neighbor,
                    "link": dict(link),
                }
            )
        return neighbors

    def validate_links(self) -> Dict[str, Any]:
        """
        Validate link consistency across the current corpus.

        Checks:
        - missing source or target objects
        - self-links
        - duplicate `(source_id, target_id, link_type)` tuples
        """
        seen = set()
        duplicate_links: List[Dict[str, str]] = []
        missing_links: List[Dict[str, str]] = []
        self_links: List[Dict[str, str]] = []

        for link in self.retrieval_backend.list_links():
            signature = (link.get("source_id"), link.get("target_id"), link.get("link_type"))
            if signature in seen:
                duplicate_links.append(link)
            else:
                seen.add(signature)

            source_id = str(link.get("source_id") or "")
            target_id = str(link.get("target_id") or "")
            if not self.retrieval_backend.get_object_by_id(source_id) or not self.retrieval_backend.get_object_by_id(target_id):
                missing_links.append(link)
            if source_id and source_id == target_id:
                self_links.append(link)

        return {
            "total_links": len(self.retrieval_backend.list_links()),
            "missing_links": missing_links,
            "self_links": self_links,
            "duplicate_links": duplicate_links,
            "is_valid": not missing_links and not self_links and not duplicate_links,
        }
