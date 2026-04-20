"""
MCP tool contracts for Agent Memory OS.

This module keeps the MCP surface thin. Retrieval lives in
``brain.services.retrieval``, while context assembly and token-budget
enforcement live in ``brain.services.context_compiler``. MCP delegates to
those services so adapters have one stable integration point.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Sequence

from brain.api.memory_api import MemoryAPI
from brain.services.retrieval import MemoryRetrievalBackend
from brain.services.writeback import MemoryWritebackBackend

class MemoryTools:
    """Core memory operations exposed to agents via MCP"""

    def __init__(
        self,
        retrieval_backend: Optional[MemoryRetrievalBackend] = None,
        writeback_backend: Optional[MemoryWritebackBackend] = None,
    ) -> None:
        """
        Initialize the MCP tool surface.

        The retrieval backend defaults to the in-memory MVP backend so the
        repository is runnable out of the box. A real storage-backed backend can
        later be injected here without changing the public tool signatures.
        """
        self.retrieval_backend = retrieval_backend or MemoryRetrievalBackend()
        self.writeback_backend = writeback_backend or MemoryWritebackBackend(self.retrieval_backend)
        self.memory_api = MemoryAPI(
            retrieval_backend=self.retrieval_backend,
            writeback_backend=self.writeback_backend,
        )

    def memory_search(self, query: str, k: int = 10, types: List[str] = None) -> List[Dict[str, Any]]:
        """
        Search the in-memory backend for relevant entries.

        This is a minimal read helper for MVP testing. It reuses the retrieval
        backend's task-oriented ranking and returns normalized dictionaries so
        callers do not need to know the underlying object family.
        """
        if not isinstance(query, str) or not query.strip():
            raise ValueError("query must be a non-empty string")
        if not isinstance(k, int) or k <= 0:
            raise ValueError("k must be a positive integer")
        return self.memory_api.search_memory(query=query, k=k, types=types)

    def memory_write(self, entry: Dict[str, Any]) -> str:
        """
        Write a new memory entry.
        Returns the entry ID.
        """
        required_fields = {"kind", "title", "summary_short", "status"}
        missing = required_fields.difference(entry)
        if missing:
            raise ValueError(f"memory_write missing required fields: {sorted(missing)}")
        return self.memory_api.write_memory_entry(entry)

    def memory_link(self, source_id: str, target_id: str, link_type: str) -> bool:
        """
        Link two memory entries.
        """
        if not all(isinstance(value, str) and value.strip() for value in (source_id, target_id, link_type)):
            raise ValueError("source_id, target_id, and link_type must be non-empty strings")
        return self.memory_api.link_memory(source_id, target_id, link_type)

    def decision_register(self, decision: Dict[str, Any]) -> str:
        """
        Register a new architectural or workflow decision.
        Returns decision ID.
        """
        required_fields = {"title", "decision", "status"}
        missing = required_fields.difference(decision)
        if missing:
            raise ValueError(f"decision_register missing required fields: {sorted(missing)}")
        return self.memory_api.register_decision(decision)

    def session_delta_write(self, delta: Dict[str, Any]) -> str:
        """
        Write session delta to memory.
        Returns delta ID.
        """
        required_fields = {"session_id", "task"}
        missing = required_fields.difference(delta)
        if missing:
            raise ValueError(f"session_delta_write missing required fields: {sorted(missing)}")
        return self.memory_api.write_session_delta(delta)

    def context_budget_report(self, context_pack: Dict[str, Any]) -> Dict[str, Any]:
        """
        Return token-budget diagnostics for an already compiled context pack.

        This keeps schema compliance intact because the canonical
        ``context_compile`` output remains unchanged; diagnostics are retrieved
        through a separate MCP method.
        """
        if not isinstance(context_pack, dict):
            raise ValueError("context_pack must be a dictionary")
        return self.memory_api.analyze_context_pack(context_pack)

    def memory_trust_report(
        self,
        types: Optional[List[str]] = None,
        include_inactive: bool = False,
    ) -> Dict[str, Any]:
        """Return a corpus-level trust and safety report."""
        return self.memory_api.trust_report(types=types, include_inactive=include_inactive)

    def memory_health_report(self) -> Dict[str, Any]:
        """Expose Phase 7 memory hygiene reporting through MCP."""
        return self.memory_api.memory_health_report()

    def memory_tier_report(self, include_inactive: bool = True) -> Dict[str, Any]:
        """Expose hot/warm/cold corpus diagnostics through MCP."""
        return self.memory_api.memory_tier_report(include_inactive=include_inactive)

    def context_optimize(
        self,
        context_pack: Dict[str, Any],
        max_total_tokens: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Return a compressed schema-shaped copy of an existing context pack."""
        if not isinstance(context_pack, dict):
            raise ValueError("context_pack must be a dictionary")
        if max_total_tokens is not None and (not isinstance(max_total_tokens, int) or max_total_tokens <= 0):
            raise ValueError("max_total_tokens must be a positive integer when provided")
        return self.memory_api.optimize_context_pack(context_pack, max_total_tokens=max_total_tokens)

    def runtime_payload_preview(self, agent: str, task: str, context_pack: Dict[str, Any]) -> Dict[str, Any]:
        """Build a stable runtime payload preview from a compiled context pack."""
        if not isinstance(agent, str) or not agent.strip():
            raise ValueError("agent must be a non-empty string")
        if not isinstance(task, str) or not task.strip():
            raise ValueError("task must be a non-empty string")
        if not isinstance(context_pack, dict):
            raise ValueError("context_pack must be a dictionary")
        return self.memory_api.build_runtime_payload(
            agent=agent,
            task=task,
            context_pack=context_pack,
        )

    def memory_snapshot_export(
        self,
        label: Optional[str] = None,
        export_kind: str = "snapshot",
    ) -> Dict[str, Any]:
        """Export the current corpus to the canonical snapshot/export storage path."""
        if export_kind not in {"snapshot", "export"}:
            raise ValueError("export_kind must be 'snapshot' or 'export'")
        return self.memory_api.export_snapshot(label=label, export_kind=export_kind)

    def memory_snapshot_import(self, snapshot_path: str, merge: bool = True) -> Dict[str, Any]:
        """Import a stored snapshot into the current in-memory backend."""
        if not isinstance(snapshot_path, str) or not snapshot_path.strip():
            raise ValueError("snapshot_path must be a non-empty string")
        return self.memory_api.import_snapshot(snapshot_path=snapshot_path, merge=merge)

    def memory_snapshot_list(self, export_kind: str = "snapshot") -> List[str]:
        """List available snapshot or export files from canonical storage."""
        if export_kind not in {"snapshot", "export"}:
            raise ValueError("export_kind must be 'snapshot' or 'export'")
        return self.memory_api.list_snapshot_files(export_kind=export_kind)

    def context_compile(self, agent: str, task: str, budget_tokens: int,
                        memory_scope: List[str] = None, repo_scope: List[str] = None) -> Dict[str, Any]:
        """
        Compile a compact ``context_pack`` for an agent and task.

        This method intentionally delegates the hard parts of ranking, pack
        assembly, and token-budget enforcement to ``ContextCompiler``. The MCP
        layer is responsible only for:

        - validating the public tool inputs
        - retrieving structured memory objects from the current backend
        - excluding archived and superseded items from the retrieval set
        - returning a dictionary that matches ``schemas/context_pack.schema.json``

        Retrieval is delegated to ``MemoryRetrievalBackend``, which already
        applies status-aware filtering, optional scope filtering, and simple
        ranking before returning structured model objects. ``ContextCompiler``
        then performs pack assembly plus strict token-budget enforcement.
        """
        if not isinstance(agent, str) or not agent.strip():
            raise ValueError("agent must be a non-empty string")
        if not isinstance(task, str) or not task.strip():
            raise ValueError("task must be a non-empty string")
        if not isinstance(budget_tokens, int) or budget_tokens <= 0:
            raise ValueError("budget_tokens must be a positive integer")

        normalized_memory_scope = self._normalize_scope(memory_scope)
        normalized_repo_scope = self._normalize_scope(repo_scope)

        return self.memory_api.compile_context(
            agent=agent,
            task=task,
            budget_tokens=budget_tokens,
            memory_scope=normalized_memory_scope,
            repo_scope=normalized_repo_scope,
        )

    def _normalize_scope(self, scope: Optional[Sequence[str]]) -> Optional[List[str]]:
        """Normalize scope filters while preserving the public MCP signature."""
        if scope is None:
            return None
        normalized = [item.strip() for item in scope if isinstance(item, str) and item.strip()]
        return normalized or None
