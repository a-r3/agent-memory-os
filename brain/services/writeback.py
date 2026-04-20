"""
In-memory writeback backend for Agent Memory OS MVP testing.

This module provides the smallest useful writeback implementation for the MVP.
It accepts structured payloads from the MCP layer, converts them into canonical
model objects, and appends them to the same in-memory collections used by the
retrieval backend.

The goal is not durable persistence. The goal is to let adapters exercise the
full compile -> execute -> writeback loop while keeping the implementation
simple, importable, and easy to replace later.
"""

from __future__ import annotations

from typing import Any, Dict, Optional, Sequence
from uuid import uuid4

from brain.models.decision import Decision
from brain.models.memory_entry import MemoryEntry
from brain.models.session_delta import SessionDelta
from brain.services.retrieval import MemoryRetrievalBackend


class MemoryWritebackBackend:
    """
    Minimal in-memory writeback backend.

    The backend shares a ``MemoryRetrievalBackend`` instance so newly written
    objects become immediately retrievable during smoke tests and adapter runs.
    """

    def __init__(self, retrieval_backend: MemoryRetrievalBackend) -> None:
        self.retrieval_backend = retrieval_backend

    def write_memory_entry(self, entry: Dict[str, Any]) -> str:
        """
        Convert an MCP memory entry payload into a ``MemoryEntry`` object.

        Important facts should carry source and status. The backend enforces only
        minimal required structure for the MVP and leaves stronger governance to
        later validation layers.
        """
        memory_entry = MemoryEntry(
            id=str(entry.get("id") or f"memory_entry:{uuid4()}"),
            kind=str(entry["kind"]),
            title=str(entry["title"]),
            summary_short=str(entry["summary_short"]),
            status=str(entry["status"]),
            created_at=entry.get("created_at"),
            updated_at=entry.get("updated_at"),
            summary_full=entry.get("summary_full"),
            tags=list(entry.get("tags") or []),
            entity_refs=list(entry.get("entity_refs") or []),
            source_refs=list(entry.get("source_refs") or []),
            confidence=entry.get("confidence"),
        )
        self.retrieval_backend.memory_entries.append(memory_entry)
        return memory_entry.id

    def register_decision(self, decision: Dict[str, Any]) -> str:
        """Convert an MCP decision payload into a canonical ``Decision`` object."""
        decision_entry = Decision(
            id=str(decision.get("id") or f"decision:{uuid4()}"),
            kind=str(decision.get("kind") or "decision"),
            title=str(decision["title"]),
            decision=str(decision["decision"]),
            status=str(decision["status"]),
            created_at=decision.get("created_at"),
            updated_at=decision.get("updated_at"),
            rationale=str(decision.get("rationale") or ""),
            affects=list(decision.get("affects") or []),
            owner=str(decision.get("owner") or ""),
            source_refs=list(decision.get("source_refs") or []),
        )
        self.retrieval_backend.decisions.append(decision_entry)
        return decision_entry.id

    def write_session_delta(self, delta: Dict[str, Any]) -> str:
        """
        Convert an MCP session delta payload into a canonical ``SessionDelta``.

        The payload is intentionally delta-based and therefore only accepts
        structured outcome fields such as new facts, decisions, artifacts, open
        questions, and next actions.
        """
        session_delta = SessionDelta(
            id=str(delta.get("id") or f"session_delta:{uuid4()}"),
            session_id=str(delta["session_id"]),
            task=str(delta["task"]),
            new_facts=list(delta.get("new_facts") or []),
            changed_facts=list(delta.get("changed_facts") or []),
            decisions=list(delta.get("decisions") or []),
            artifacts=list(delta.get("artifacts") or []),
            open_questions=list(delta.get("open_questions") or []),
            next_actions=list(delta.get("next_actions") or []),
            created_at=delta.get("created_at"),
        )
        self.retrieval_backend.session_deltas.append(session_delta)
        return session_delta.id

    def link_entries(self, source_id: str, target_id: str, link_type: str) -> bool:
        """
        Record a typed link between two existing objects.

        The MVP stores link records as dictionaries inside the shared in-memory
        backend. This keeps linking functional before a dedicated graph/link
        model is introduced in later roadmap phases.
        """
        if not self.retrieval_backend.has_object(source_id):
            raise ValueError(f"source_id not found: {source_id}")
        if not self.retrieval_backend.has_object(target_id):
            raise ValueError(f"target_id not found: {target_id}")

        record = {
            "id": f"link:{uuid4()}",
            "source_id": source_id,
            "target_id": target_id,
            "link_type": link_type,
        }
        self.retrieval_backend.links.append(record)
        return True
