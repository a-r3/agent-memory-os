"""
Ranking utilities for Agent Memory OS retrieval.

This service centralizes retrieval scoring so relevance policy can evolve
without spreading ranking heuristics across MCP, adapters, and memory API.
"""

from __future__ import annotations

from datetime import datetime, UTC
from typing import Any


class RetrievalRankingService:
    """
    Compute deterministic scores for memory objects.

    The current implementation combines:
    - reusable-memory priority for rules and identity
    - direct task-term overlap
    - link-aware relationship bonus
    - modest trust weighting from status
    - a small type bonus for entities
    """

    def score_item(
        self,
        *,
        fields: dict[str, Any],
        item_type: str,
        task_terms: set[str],
        searchable_terms: set[str],
        relationship_bonus: float = 0.0,
    ) -> float:
        kind = str(fields.get("kind") or "").casefold()
        tags = {tag.casefold() for tag in fields.get("tags") or []}
        status = str(fields.get("status") or "").casefold()

        reusable_bonus = 0.0
        if kind == "rule" or "rule" in tags:
            reusable_bonus += 25
        if kind == "identity" or "identity" in tags:
            reusable_bonus += 20
        if kind in {"procedure", "workflow"} or "procedure" in tags or "tool" in tags:
            reusable_bonus += 10

        overlap_score = len(task_terms.intersection(searchable_terms)) * 8

        status_bonus = 0.0
        if status == "approved":
            status_bonus = 12
        elif status == "verified":
            status_bonus = 8
        elif status == "unverified":
            status_bonus = 3

        provenance_bonus = 4 if fields.get("source_refs") else 0

        confidence_bonus = 0.0
        confidence = fields.get("confidence")
        if isinstance(confidence, (int, float)):
            confidence_bonus = max(0.0, min(6.0, confidence * 6.0))

        recency_bonus = self._recency_bonus(fields)
        type_bonus = 2 if item_type == "entity" else 0
        return (
            reusable_bonus
            + overlap_score
            + relationship_bonus
            + status_bonus
            + provenance_bonus
            + confidence_bonus
            + recency_bonus
            + type_bonus
        )

    def _recency_bonus(self, fields: dict[str, Any]) -> float:
        """Reward recent updates modestly without overwhelming reusable memory."""
        timestamp = fields.get("updated_at") or fields.get("created_at")
        if not isinstance(timestamp, str) or not timestamp.strip():
            return 0.0
        try:
            parsed = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        except ValueError:
            return 0.0
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=UTC)

        age_days = max(0.0, (datetime.now(UTC) - parsed).total_seconds() / 86400.0)
        if age_days <= 1:
            return 4.0
        if age_days <= 7:
            return 2.0
        return 0.0
