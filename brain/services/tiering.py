"""
Hot/warm/cold tier classification for Agent Memory OS.

The tiering service gives the optimization layer a deterministic view of which
objects are most likely to be reused. This supports cost-aware retrieval,
cache-friendly prompt construction, and operational reporting.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict

if TYPE_CHECKING:
    from brain.api.memory_api import MemoryAPI


class MemoryTieringService:
    """Classify memory objects into hot, warm, and cold tiers."""

    def __init__(self, memory_api: "MemoryAPI") -> None:
        self.memory_api = memory_api

    def classify_item(self, item: Dict[str, Any], *, link_count: int = 0) -> str:
        """Return a deterministic tier label for one normalized memory object."""
        data = item.get("data", {})
        status = str(item.get("status") or "").casefold()
        kind = str(data.get("kind") or "").casefold()
        confidence = data.get("confidence")

        if status in {"archived", "superseded"}:
            return "cold"

        if kind in {"rule", "identity"}:
            return "hot"
        if item.get("type") == "decision" and status in {"approved", "verified"}:
            return "hot"
        if isinstance(confidence, (int, float)) and confidence >= 0.8:
            return "hot"
        if link_count >= 2:
            return "hot"
        return "warm"

    def build_tier_report(self, *, include_inactive: bool = True) -> Dict[str, Any]:
        """Summarize the current corpus by optimization tier."""
        objects = self.memory_api.list_objects(include_inactive=include_inactive)
        links = self.memory_api.list_links()
        link_counts: dict[str, int] = {}
        for link in links:
            source_id = str(link.get("source_id") or "")
            target_id = str(link.get("target_id") or "")
            if source_id:
                link_counts[source_id] = link_counts.get(source_id, 0) + 1
            if target_id:
                link_counts[target_id] = link_counts.get(target_id, 0) + 1

        counts = {"hot": 0, "warm": 0, "cold": 0}
        examples = {"hot": [], "warm": [], "cold": []}
        for item in objects:
            tier = self.classify_item(item, link_count=link_counts.get(item["id"], 0))
            counts[tier] += 1
            if len(examples[tier]) < 5:
                examples[tier].append(item["id"])

        return {
            "counts": counts,
            "examples": examples,
            "total_objects": len(objects),
        }
