"""
Canonical memory API facade for Agent Memory OS.

This module is the Phase 2 memory-core entrypoint described in the roadmap. It
coordinates retrieval, writeback, linking, and context compilation while
keeping those responsibilities implemented in their dedicated services.

The API is intentionally small:

- search existing memory
- write new memory entries
- register decisions
- write session deltas
- create typed links
- compile context packs

It is designed to be reused by MCP and any future internal services while
preserving the central architecture rule that compiled context and durable
writeback remain system responsibilities.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Sequence

from brain.services.budgeting import BudgetingService
from brain.services.context_compiler import ContextCompiler
from brain.services.context_pack_validation import ContextPackValidator
from brain.services.memory_hygiene import MemoryHygieneService
from brain.services.persistence import PersistenceService
from brain.services.retrieval import MemoryRetrievalBackend
from brain.services.summarization import SummarizationService
from brain.services.tiering import MemoryTieringService
from brain.services.trust import TrustService
from brain.services.writeback import MemoryWritebackBackend


class MemoryAPI:
    """
    Minimal canonical memory API.

    Retrieval, compilation, and writeback remain centralized in their own
    services. This facade binds them into one internal interface consistent
    with the roadmap and ready for storage-backed replacement later.
    """

    def __init__(
        self,
        *,
        retrieval_backend: Optional[MemoryRetrievalBackend] = None,
        writeback_backend: Optional[MemoryWritebackBackend] = None,
        context_compiler: Optional[ContextCompiler] = None,
        context_pack_validator: Optional[ContextPackValidator] = None,
        trust_service: Optional[TrustService] = None,
        budgeting_service: Optional[BudgetingService] = None,
        summarization_service: Optional[SummarizationService] = None,
        persistence_service: Optional[PersistenceService] = None,
    ) -> None:
        self.retrieval_backend = retrieval_backend or MemoryRetrievalBackend()
        self.writeback_backend = writeback_backend or MemoryWritebackBackend(self.retrieval_backend)
        self.context_compiler = context_compiler or ContextCompiler()
        self.context_pack_validator = context_pack_validator or ContextPackValidator()
        self.trust_service = trust_service or TrustService()
        self.budgeting_service = budgeting_service or BudgetingService(
            token_estimator=self.context_compiler.token_estimator,
            reserved_output_ratio=self.context_compiler.config.reserved_output_ratio,
            minimum_output_tokens=self.context_compiler.config.minimum_output_tokens,
            minimum_input_tokens=self.context_compiler.config.minimum_input_tokens,
        )
        self.summarization_service = summarization_service or SummarizationService(
            token_estimator=self.context_compiler.token_estimator
        )
        self.persistence_service = persistence_service or PersistenceService()
        self.memory_hygiene_service = MemoryHygieneService(self)
        self.memory_tiering_service = MemoryTieringService(self)

    def search_memory(
        self,
        *,
        query: str,
        k: int = 10,
        types: Optional[Sequence[str]] = None,
        memory_scope: Optional[Sequence[str]] = None,
        repo_scope: Optional[Sequence[str]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Search across the canonical in-memory corpus and normalize results.

        The API relies on globally ranked retrieval from ``MemoryRetrievalBackend``
        so callers receive a top-k list across object families rather than a
        concatenation of per-type slices.
        """
        candidates = self.retrieval_backend.search(
            task=query,
            k=k,
            types=types,
            memory_scope=memory_scope,
            repo_scope=repo_scope,
        )
        return [self.normalize_object(candidate.item, candidate.item_type) for candidate in candidates]

    def write_memory_entry(self, entry: Dict[str, Any]) -> str:
        """Write a new memory entry through the canonical writeback backend."""
        validation = self.trust_service.validate_write_payload(payload_type="memory_entry", payload=entry)
        if not validation["allowed"]:
            raise ValueError(f"memory_entry write blocked: {validation['blockers']}")
        return self.writeback_backend.write_memory_entry(entry)

    def register_decision(self, decision: Dict[str, Any]) -> str:
        """Register a decision through the canonical writeback backend."""
        validation = self.trust_service.validate_write_payload(payload_type="decision", payload=decision)
        if not validation["allowed"]:
            raise ValueError(f"decision write blocked: {validation['blockers']}")
        return self.writeback_backend.register_decision(decision)

    def write_session_delta(self, delta: Dict[str, Any]) -> str:
        """Write a session delta through the canonical writeback backend."""
        validation = self.trust_service.validate_write_payload(payload_type="session_delta", payload=delta)
        if not validation["allowed"]:
            raise ValueError(f"session_delta write blocked: {validation['blockers']}")
        return self.writeback_backend.write_session_delta(delta)

    def link_memory(self, source_id: str, target_id: str, link_type: str) -> bool:
        """Create a typed relationship between two existing memory objects."""
        return self.writeback_backend.link_entries(source_id, target_id, link_type)

    def compile_context(
        self,
        *,
        agent: str,
        task: str,
        budget_tokens: int,
        memory_scope: Optional[Sequence[str]] = None,
        repo_scope: Optional[Sequence[str]] = None,
    ) -> Dict[str, Any]:
        """
        Compile and validate a schema-shaped ``context_pack``.

        Retrieval remains centralized in the retrieval backend and token-budget
        enforcement remains centralized in ``ContextCompiler``.
        """
        priority_ids = self._relationship_priority_ids(
            task=task,
            memory_scope=memory_scope,
            repo_scope=repo_scope,
        )
        context_pack = self.context_compiler.compile_context_pack(
            agent=agent,
            task=task,
            budget_tokens=budget_tokens,
            memory_entries=self.retrieval_backend.get_memory_entries(
                task=task,
                memory_scope=memory_scope,
                repo_scope=repo_scope,
            ),
            decisions=self.retrieval_backend.get_decisions(
                task=task,
                memory_scope=memory_scope,
                repo_scope=repo_scope,
            ),
            session_deltas=self.retrieval_backend.get_session_deltas(
                task=task,
                memory_scope=memory_scope,
                repo_scope=repo_scope,
            ),
            entities=self.retrieval_backend.get_entities(
                task=task,
                memory_scope=memory_scope,
                repo_scope=repo_scope,
            ),
            memory_scope=memory_scope,
            repo_scope=repo_scope,
            priority_ids=priority_ids,
        )
        return self.context_pack_validator.validate(context_pack)

    def analyze_context_pack(self, context_pack: Dict[str, Any]) -> Dict[str, Any]:
        """Return budget diagnostics for an already-compiled context pack."""
        return self.budgeting_service.analyze_context_pack(context_pack)

    def trust_report(
        self,
        *,
        types: Optional[Sequence[str]] = None,
        include_inactive: bool = False,
    ) -> Dict[str, Any]:
        """Audit the current corpus for trust and safety issues."""
        objects = self.retrieval_backend.list_objects(types=types, include_inactive=include_inactive)
        return self.trust_service.audit_items(objects)

    def memory_health_report(self) -> Dict[str, Any]:
        """Expose Phase 7 hygiene diagnostics through the canonical API."""
        return self.memory_hygiene_service.generate_health_report()

    def optimize_context_pack(
        self,
        context_pack: Dict[str, Any],
        *,
        max_total_tokens: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Compress an existing context pack while preserving schema shape."""
        optimized = self.summarization_service.compress_context_pack(
            context_pack,
            max_total_tokens=max_total_tokens,
        )
        return self.context_pack_validator.validate(optimized)

    def build_runtime_payload(
        self,
        *,
        agent: str,
        task: str,
        context_pack: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Build a stable runtime payload from a compiled context pack."""
        self.context_pack_validator.validate(context_pack)
        return self.summarization_service.build_runtime_payload(
            agent=agent,
            task=task,
            context_pack=context_pack,
        )

    def memory_tier_report(self, *, include_inactive: bool = True) -> Dict[str, Any]:
        """Return hot/warm/cold tier diagnostics for the current corpus."""
        return self.memory_tiering_service.build_tier_report(include_inactive=include_inactive)

    def export_snapshot(self, *, label: Optional[str] = None, export_kind: str = "snapshot") -> Dict[str, Any]:
        """Export the current corpus to the canonical storage snapshot path."""
        return self.persistence_service.export_snapshot(
            self.retrieval_backend,
            label=label,
            export_kind=export_kind,
        )

    def import_snapshot(self, *, snapshot_path: str, merge: bool = True) -> Dict[str, Any]:
        """Import a stored snapshot back into the in-memory backend."""
        return self.persistence_service.import_snapshot(
            self.retrieval_backend,
            snapshot_path=snapshot_path,
            merge=merge,
        )

    def list_snapshot_files(self, *, export_kind: str = "snapshot") -> List[str]:
        """List known snapshot or export files from canonical storage."""
        return self.persistence_service.list_snapshot_files(export_kind=export_kind)

    def get_links_for_id(self, object_id: str) -> List[dict[str, str]]:
        """Return all current link records involving the given id."""
        return self.retrieval_backend.get_links_for_id(object_id)

    def list_links(self) -> List[dict[str, str]]:
        """Return the full current link registry."""
        return self.retrieval_backend.list_links()

    def get_object_by_id(self, object_id: str) -> Any | None:
        """Fetch a raw canonical object by id."""
        return self.retrieval_backend.get_object_by_id(object_id)

    def list_objects(
        self,
        *,
        types: Optional[Sequence[str]] = None,
        include_inactive: bool = False,
    ) -> List[Dict[str, Any]]:
        """List normalized objects from the canonical in-memory corpus."""
        objects = self.retrieval_backend.list_objects(types=types, include_inactive=include_inactive)
        return [self.normalize_object(item) for item in objects]

    def normalize_object(self, item: Any, item_type: Optional[str] = None) -> Dict[str, Any]:
        """Normalize a model object for API consumers."""
        resolved_item_type = item_type or self._infer_item_type(item)
        fields = vars(item)
        return {
            "id": fields.get("id"),
            "type": resolved_item_type,
            "kind": fields.get("kind"),
            "title": fields.get("title") or fields.get("name") or fields.get("task"),
            "status": fields.get("status"),
            "data": dict(fields),
        }

    def _infer_item_type(self, item: Any) -> str:
        fields = vars(item)
        if "summary_short" in fields:
            return "memory_entry"
        if "decision" in fields and "affects" in fields:
            return "decision"
        if "session_id" in fields:
            return "session_delta"
        return "entity"

    def _relationship_priority_ids(
        self,
        *,
        task: str,
        memory_scope: Optional[Sequence[str]],
        repo_scope: Optional[Sequence[str]],
    ) -> List[str]:
        """
        Derive a small relationship-aware priority set for context compilation.

        The method starts from the top search anchors for the task and adds their
        directly linked neighbors. ``ContextCompiler`` can then favor those ids
        without duplicating relationship traversal logic.
        """
        anchors = self.retrieval_backend.search(
            task=task,
            k=5,
            memory_scope=memory_scope,
            repo_scope=repo_scope,
        )
        priority_ids = {self._stable_id(candidate.item) for candidate in anchors}
        for candidate in anchors:
            object_id = self._stable_id(candidate.item)
            for link in self.retrieval_backend.get_links_for_id(object_id):
                neighbor_id = link["target_id"] if link.get("source_id") == object_id else link.get("source_id")
                if neighbor_id:
                    priority_ids.add(neighbor_id)
        return sorted(priority_ids)

    def _stable_id(self, item: Any) -> str:
        return str(vars(item).get("id") or "")
