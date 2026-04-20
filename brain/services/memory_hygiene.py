"""
Memory hygiene services for Agent Memory OS.

This module implements the first Phase 7 hygiene layer:

- promotion suggestions from repeated structured delta content
- duplicate candidate detection across durable objects
- link validation for consistency and drift detection
- memory health reporting suitable for monitoring and audits

All reads go through ``MemoryAPI`` so the hygiene layer does not bypass the
canonical memory facade.
"""

from __future__ import annotations

from collections import Counter, defaultdict
import hashlib
from typing import TYPE_CHECKING, Any, Dict, List

from brain.services.linking import LinkingService

if TYPE_CHECKING:
    from brain.api.memory_api import MemoryAPI


class MemoryHygieneService:
    """Phase 7 hygiene and reporting utilities."""

    def __init__(self, memory_api: "MemoryAPI") -> None:
        self.memory_api = memory_api
        self.linking_service = LinkingService(memory_api.retrieval_backend)

    def suggest_promotions(self, minimum_frequency: int = 2) -> List[Dict[str, Any]]:
        """
        Suggest promotion candidates from repeated session delta content.

        The MVP has no dedicated working-memory model yet, so repeated facts or
        decisions inside session deltas are treated as candidates for durable
        promotion into long-term memory.
        """
        frequency: Counter[str] = Counter()
        evidence: defaultdict[str, list[str]] = defaultdict(list)

        for result in self.memory_api.list_objects(types=["session_delta"]):
            data = result["data"]
            source_id = result["id"]
            for field_name in ("new_facts", "changed_facts", "decisions"):
                for value in data.get(field_name, []):
                    normalized = self._normalize_text(str(value))
                    if not normalized:
                        continue
                    frequency[normalized] += 1
                    evidence[normalized].append(source_id)

        promotions: List[Dict[str, Any]] = []
        for text, count in frequency.items():
            if count < minimum_frequency:
                continue
            promotions.append(
                {
                    "candidate_text": text,
                    "occurrences": count,
                    "evidence_session_ids": sorted(set(evidence[text])),
                    "suggested_action": "promote_to_memory_entry",
                }
            )

        promotions.sort(key=lambda item: (-item["occurrences"], item["candidate_text"]))
        return promotions

    def find_duplicate_candidates(self) -> List[Dict[str, Any]]:
        """
        Find likely duplicate durable objects using normalized signatures.

        The service does not mutate memory yet. It returns candidate groups so a
        later merge/archive flow can act on them intentionally.
        """
        signatures: defaultdict[str, list[Dict[str, Any]]] = defaultdict(list)
        for result in self.memory_api.list_objects(types=["memory_entry", "decision", "entity"]):
            data = result["data"]
            signature = self._signature(
                result["type"],
                str(result["title"] or ""),
                self._signature_body(data),
            )
            signatures[signature].append(result)

        duplicates: List[Dict[str, Any]] = []
        for signature, items in signatures.items():
            if len(items) < 2:
                continue
            duplicates.append(
                {
                    "signature": signature,
                    "count": len(items),
                    "ids": [item["id"] for item in items],
                    "titles": [item["title"] for item in items],
                }
            )

        duplicates.sort(key=lambda item: (-item["count"], item["signature"]))
        return duplicates

    def validate_links(self) -> Dict[str, Any]:
        """
        Validate link consistency across the current in-memory link registry.
        """
        return self.linking_service.validate_links()

    def generate_health_report(self) -> Dict[str, Any]:
        """
        Generate a compact health report for the current memory corpus.

        The report is monitoring-oriented and summarizes object counts, status
        distribution, duplicate candidates, promotion candidates, and link
        consistency.
        """
        objects = self.memory_api.list_objects(include_inactive=True)
        by_type = Counter(item["type"] for item in objects)
        by_status = Counter((item.get("status") or "unknown") for item in objects)
        duplicate_candidates = self.find_duplicate_candidates()
        promotion_candidates = self.suggest_promotions()
        link_validation = self.validate_links()

        return {
            "total_objects": len(objects),
            "objects_by_type": dict(by_type),
            "objects_by_status": dict(by_status),
            "duplicate_candidate_groups": len(duplicate_candidates),
            "promotion_candidate_groups": len(promotion_candidates),
            "link_validation": link_validation,
            "duplicate_candidates": duplicate_candidates,
            "promotion_candidates": promotion_candidates,
        }

    def _signature_body(self, data: Dict[str, Any]) -> str:
        if "summary_short" in data:
            return self._normalize_text(f"{data.get('summary_short', '')} {data.get('summary_full', '')}")
        if "decision" in data:
            return self._normalize_text(f"{data.get('decision', '')} {data.get('rationale', '')}")
        if "description" in data:
            return self._normalize_text(data.get("description", ""))
        return ""

    def _signature(self, item_type: str, title: str, body: str) -> str:
        raw = f"{item_type}|{self._normalize_text(title)}|{body}"
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def _normalize_text(self, text: str) -> str:
        return " ".join(text.casefold().split())
