"""
Trust and safety checks for Agent Memory OS.

This service implements later-phase governance controls described in the
architecture:

- trust-aware write validation
- lightweight secret/PII detection
- corpus-level trust auditing

The implementation is intentionally local and deterministic so it can be used
from the canonical ``MemoryAPI`` without introducing external dependencies.
It does not replace stronger downstream governance, but it provides a useful
MVP guardrail for memory writes and retrieval diagnostics.
"""

from __future__ import annotations

from collections import Counter
import re
from typing import Any, Iterable, Mapping


SECRET_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("openai_key", re.compile(r"\bsk-[A-Za-z0-9]{20,}\b")),
    ("aws_access_key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    (
        "generic_secret_assignment",
        re.compile(
            r"\b(api[_-]?key|secret|token|password)\b\s*[:=]\s*['\"]?[A-Za-z0-9_\-\/+=]{8,}",
            flags=re.IGNORECASE,
        ),
    ),
)

PII_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("email_address", re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", flags=re.IGNORECASE)),
)

STATUS_SCORES = {
    "approved": 25,
    "verified": 18,
    "unverified": 0,
    "draft": -5,
    "pending": -5,
    "archived": -20,
    "superseded": -20,
}


class TrustService:
    """
    Evaluate memory objects for provenance and safety.

    The service is designed to sit behind ``MemoryAPI`` so MCP and adapters can
    use the same governance path as future internal callers. Missing source
    attribution is treated as a warning rather than a hard failure; secret-like
    content is treated as a write blocker.
    """

    def validate_write_payload(self, *, payload_type: str, payload: Mapping[str, Any]) -> dict[str, Any]:
        """
        Validate a structured write payload before it enters durable memory.

        The validator allows normal MVP writes while blocking obvious secret-like
        content. Missing provenance is reported as a warning so current callers
        remain compatible with the existing scaffold.
        """
        warnings: list[str] = []
        blockers: list[str] = []

        scan = self.scan_text_fields(payload)
        blockers.extend(scan["blockers"])
        warnings.extend(scan["warnings"])

        if payload_type in {"memory_entry", "decision"} and not list(payload.get("source_refs") or []):
            warnings.append("missing_source_refs")
        if payload_type == "memory_entry" and payload.get("status") in {"approved", "verified"} and payload.get("confidence") is None:
            warnings.append("missing_confidence_for_high_status")

        return {
            "allowed": not blockers,
            "payload_type": payload_type,
            "warnings": sorted(set(warnings)),
            "blockers": sorted(set(blockers)),
        }

    def assess_item(self, item: Any) -> dict[str, Any]:
        """
        Produce a normalized trust assessment for a stored object.

        The score is intentionally simple and deterministic. It combines status,
        provenance, confidence, and secret/PII detection into a single summary
        that can be surfaced in reports or used by later retrieval policy.
        """
        fields = self._fields(item)
        warnings: list[str] = []
        blockers: list[str] = []
        score = 50

        status = str(fields.get("status") or "unverified").casefold()
        score += STATUS_SCORES.get(status, 0)

        if list(fields.get("source_refs") or []):
            score += 10
        else:
            warnings.append("missing_source_refs")

        confidence = fields.get("confidence")
        if isinstance(confidence, (int, float)):
            if confidence >= 0.8:
                score += 10
            elif confidence >= 0.6:
                score += 5
            elif confidence < 0.3:
                score -= 10
                warnings.append("low_confidence")

        scan = self.scan_text_fields(fields)
        blockers.extend(scan["blockers"])
        warnings.extend(scan["warnings"])
        if blockers:
            score = 0

        trust_level = "low"
        if blockers:
            trust_level = "restricted"
        elif score >= 80:
            trust_level = "high"
        elif score >= 60:
            trust_level = "medium"

        return {
            "id": str(fields.get("id") or ""),
            "score": max(0, min(100, score)),
            "trust_level": trust_level,
            "warnings": sorted(set(warnings)),
            "blockers": sorted(set(blockers)),
        }

    def audit_items(self, items: Iterable[Any]) -> dict[str, Any]:
        """Aggregate trust assessments across a collection of memory objects."""
        assessments = [self.assess_item(item) for item in items]
        level_counts = Counter(assessment["trust_level"] for assessment in assessments)
        flagged = [assessment for assessment in assessments if assessment["warnings"] or assessment["blockers"]]
        return {
            "total_items": len(assessments),
            "trust_levels": dict(level_counts),
            "flagged_items": flagged,
            "blocked_item_ids": [assessment["id"] for assessment in assessments if assessment["blockers"]],
        }

    def scan_text_fields(self, payload: Mapping[str, Any] | Any) -> dict[str, list[str]]:
        """Scan all textual content in a payload for obvious secret or PII patterns."""
        text = " ".join(self._iter_text_values(payload))
        blockers: list[str] = []
        warnings: list[str] = []

        for label, pattern in SECRET_PATTERNS:
            if pattern.search(text):
                blockers.append(f"detected_{label}")

        for label, pattern in PII_PATTERNS:
            if pattern.search(text):
                warnings.append(f"detected_{label}")

        return {
            "blockers": blockers,
            "warnings": warnings,
        }

    def _iter_text_values(self, payload: Mapping[str, Any] | Any) -> Iterable[str]:
        fields = self._fields(payload)
        for value in fields.values():
            yield from self._flatten_text(value)

    def _flatten_text(self, value: Any) -> Iterable[str]:
        if isinstance(value, str):
            if value.strip():
                yield value
            return
        if isinstance(value, Mapping):
            for nested in value.values():
                yield from self._flatten_text(nested)
            return
        if isinstance(value, (list, tuple, set)):
            for nested in value:
                yield from self._flatten_text(nested)

    def _fields(self, payload: Mapping[str, Any] | Any) -> dict[str, Any]:
        if isinstance(payload, Mapping):
            return dict(payload)
        return dict(vars(payload))
