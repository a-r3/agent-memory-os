"""
In-memory retrieval backend for the Agent Memory OS MVP.

This module is the canonical stub retrieval service for early integration and
smoke testing. It returns typed model objects and applies a minimal but useful
retrieval pipeline:

1. start from in-memory sample objects or explicitly injected objects
2. drop inactive records such as archived or superseded items
3. apply optional ``memory_scope`` and ``repo_scope`` allow-lists
4. rank remaining objects using reusable-priority plus task-term overlap
5. return Python model instances ready for ``ContextCompiler``

This is intentionally not a persistent backend. It should be replaced later by
real document, vector, and graph-backed retrieval while preserving the same
high-level contracts used by MCP and adapters.
"""

from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Any, List, Optional, Sequence

from brain.models.decision import Decision
from brain.models.entity import Entity
from brain.models.memory_entry import MemoryEntry
from brain.models.session_delta import SessionDelta
from brain.services.linking import LinkingService
from brain.services.ranking import RetrievalRankingService


INACTIVE_STATUSES = {"archived", "superseded"}


@dataclass(frozen=True)
class RetrievalCandidate:
    """Internal scoring wrapper used to produce deterministic ordering."""

    item: Any
    score: float
    item_type: str


class MemoryRetrievalBackend:
    """
    Minimal in-memory retrieval backend.

    All retrieval methods return the canonical model objects defined in
    ``brain/models`` so callers can pass results directly into
    ``ContextCompiler.compile_context_pack(...)`` without any adaptation layer.
    """

    def __init__(
        self,
        *,
        memory_entries: Optional[Sequence[MemoryEntry]] = None,
        decisions: Optional[Sequence[Decision]] = None,
        session_deltas: Optional[Sequence[SessionDelta]] = None,
        entities: Optional[Sequence[Entity]] = None,
        links: Optional[Sequence[dict[str, str]]] = None,
    ) -> None:
        samples = self._sample_data()
        self.memory_entries = list(memory_entries or samples["memory_entries"])
        self.decisions = list(decisions or samples["decisions"])
        self.session_deltas = list(session_deltas or samples["session_deltas"])
        self.entities = list(entities or samples["entities"])
        self.links = list(links or [])
        self.linking_service = LinkingService(self)
        self.ranking_service = RetrievalRankingService()

    def get_memory_entries(
        self,
        *,
        task: str,
        memory_scope: Optional[Sequence[str]] = None,
        repo_scope: Optional[Sequence[str]] = None,
        limit: Optional[int] = None,
    ) -> List[MemoryEntry]:
        """
        Retrieve active ``MemoryEntry`` objects for a task.

        Rules and identity entries receive a reusable-priority bonus so they
        stay competitive even when the task text is narrow.
        """
        return self._retrieve(
            items=self.memory_entries,
            task=task,
            memory_scope=memory_scope,
            repo_scope=repo_scope,
            limit=limit,
        )

    def get_decisions(
        self,
        *,
        task: str,
        memory_scope: Optional[Sequence[str]] = None,
        repo_scope: Optional[Sequence[str]] = None,
        limit: Optional[int] = None,
    ) -> List[Decision]:
        """Retrieve active ``Decision`` objects for a task."""
        return self._retrieve(
            items=self.decisions,
            task=task,
            memory_scope=memory_scope,
            repo_scope=repo_scope,
            limit=limit,
        )

    def get_session_deltas(
        self,
        *,
        task: str,
        memory_scope: Optional[Sequence[str]] = None,
        repo_scope: Optional[Sequence[str]] = None,
        limit: Optional[int] = None,
    ) -> List[SessionDelta]:
        """
        Retrieve active ``SessionDelta`` objects for a task.

        Only structured delta fields are used; the backend does not model or
        return raw transcript history.
        """
        return self._retrieve(
            items=self.session_deltas,
            task=task,
            memory_scope=memory_scope,
            repo_scope=repo_scope,
            limit=limit,
        )

    def get_entities(
        self,
        *,
        task: str,
        memory_scope: Optional[Sequence[str]] = None,
        repo_scope: Optional[Sequence[str]] = None,
        limit: Optional[int] = None,
    ) -> List[Entity]:
        """Retrieve semantic ``Entity`` objects for a task."""
        return self._retrieve(
            items=self.entities,
            task=task,
            memory_scope=memory_scope,
            repo_scope=repo_scope,
            limit=limit,
        )

    def search(
        self,
        *,
        task: str,
        k: int = 10,
        types: Optional[Sequence[str]] = None,
        memory_scope: Optional[Sequence[str]] = None,
        repo_scope: Optional[Sequence[str]] = None,
    ) -> List[RetrievalCandidate]:
        """
        Search across all object families with global ranking.

        This keeps cross-type search logic centralized in retrieval instead of
        duplicating ranking behavior in the MCP layer.
        """
        if k <= 0:
            return []

        allowed_types = {item.strip().casefold() for item in (types or []) if isinstance(item, str) and item.strip()}
        candidates: List[RetrievalCandidate] = []

        if not allowed_types or allowed_types.intersection({"memory_entry", "memory", "entry"}):
            candidates.extend(
                self._retrieve_candidates(
                    items=self.memory_entries,
                    item_type="memory_entry",
                    task=task,
                    memory_scope=memory_scope,
                    repo_scope=repo_scope,
                )
            )
        if not allowed_types or allowed_types.intersection({"decision", "decisions"}):
            candidates.extend(
                self._retrieve_candidates(
                    items=self.decisions,
                    item_type="decision",
                    task=task,
                    memory_scope=memory_scope,
                    repo_scope=repo_scope,
                )
            )
        if not allowed_types or allowed_types.intersection({"session_delta", "delta", "session"}):
            candidates.extend(
                self._retrieve_candidates(
                    items=self.session_deltas,
                    item_type="session_delta",
                    task=task,
                    memory_scope=memory_scope,
                    repo_scope=repo_scope,
                )
            )
        if not allowed_types or allowed_types.intersection({"entity", "entities"}):
            candidates.extend(
                self._retrieve_candidates(
                    items=self.entities,
                    item_type="entity",
                    task=task,
                    memory_scope=memory_scope,
                    repo_scope=repo_scope,
                )
            )

        candidates.sort(
            key=lambda candidate: (-candidate.score, candidate.item_type, self._stable_identifier(candidate.item))
        )
        return candidates[:k]

    def get_links_for_id(self, object_id: str) -> List[dict[str, str]]:
        """Return link records that mention the provided object id."""
        object_id = object_id.strip()
        return [
            dict(link)
            for link in self.links
            if link.get("source_id") == object_id or link.get("target_id") == object_id
        ]

    def list_links(self) -> List[dict[str, str]]:
        """Return all known link records."""
        return [dict(link) for link in self.links]

    def has_object(self, object_id: str) -> bool:
        """Check whether an id exists in the current in-memory corpus."""
        return any(
            self._stable_identifier(item) == object_id
            for item in [*self.memory_entries, *self.decisions, *self.session_deltas, *self.entities]
        )

    def get_object_by_id(self, object_id: str) -> Any | None:
        """Fetch an object by id from the current in-memory corpus."""
        for item in [*self.memory_entries, *self.decisions, *self.session_deltas, *self.entities]:
            if self._stable_identifier(item) == object_id:
                return item
        return None

    def list_objects(
        self,
        *,
        types: Optional[Sequence[str]] = None,
        include_inactive: bool = False,
    ) -> List[Any]:
        """List objects from the in-memory corpus with optional type filtering."""
        allowed_types = {item.strip().casefold() for item in (types or []) if isinstance(item, str) and item.strip()}
        objects: List[Any] = []

        type_sets = (
            ("memory_entry", self.memory_entries),
            ("decision", self.decisions),
            ("session_delta", self.session_deltas),
            ("entity", self.entities),
        )
        for item_type, items in type_sets:
            aliases = {
                "memory_entry": {"memory_entry", "memory", "entry"},
                "decision": {"decision", "decisions"},
                "session_delta": {"session_delta", "delta", "session"},
                "entity": {"entity", "entities"},
            }[item_type]
            if allowed_types and not allowed_types.intersection(aliases):
                continue
            for item in items:
                status = str(getattr(item, "status", "") or "").casefold()
                if not include_inactive and status in INACTIVE_STATUSES:
                    continue
                objects.append(item)

        objects.sort(key=self._stable_identifier)
        return objects

    def _retrieve(
        self,
        *,
        items: Sequence[Any],
        task: str,
        memory_scope: Optional[Sequence[str]],
        repo_scope: Optional[Sequence[str]],
        limit: Optional[int],
    ) -> List[Any]:
        """
        Shared retrieval pipeline for all object families.

        Filtering and ranking are intentionally simple and deterministic:
        - inactive statuses are dropped first
        - ``memory_scope`` filters on kinds/tags
        - ``repo_scope`` filters on names, refs, and links
        - task-term overlap and reusable memory bonuses determine ordering
        """
        candidates = self._retrieve_candidates(
            items=items,
            item_type="generic",
            task=task,
            memory_scope=memory_scope,
            repo_scope=repo_scope,
        )
        results = [candidate.item for candidate in candidates]
        return results[:limit] if limit is not None else results

    def _retrieve_candidates(
        self,
        *,
        items: Sequence[Any],
        item_type: str,
        task: str,
        memory_scope: Optional[Sequence[str]],
        repo_scope: Optional[Sequence[str]],
    ) -> List[RetrievalCandidate]:
        """Return ranked candidates while preserving score metadata."""
        task_terms = _term_set(task)
        memory_scope_terms = _term_set(" ".join(memory_scope or []))
        repo_scope_terms = _term_set(" ".join(repo_scope or []))
        ranked: List[RetrievalCandidate] = []

        for item in items:
            fields = vars(item)
            status = str(fields.get("status") or "").strip().casefold()
            if status in INACTIVE_STATUSES:
                continue

            memory_terms = self._memory_scope_terms(fields)
            repo_terms = self._repo_scope_terms(fields)
            searchable_terms = self._searchable_terms(fields)

            if memory_scope_terms and not memory_terms.intersection(memory_scope_terms):
                continue
            if repo_scope_terms and not repo_terms.intersection(repo_scope_terms):
                continue

            ranked.append(
                RetrievalCandidate(
                    item=item,
                    score=self._score_item(
                        fields=fields,
                        item_type=item_type,
                        task_terms=task_terms,
                        searchable_terms=searchable_terms,
                    ),
                    item_type=item_type,
                )
            )

        ranked.sort(
            key=lambda candidate: (-candidate.score, candidate.item_type, self._stable_identifier(candidate.item))
        )
        return ranked

    def _memory_scope_terms(self, fields: dict[str, Any]) -> set[str]:
        """Terms used to filter by memory layer or object family."""
        return _term_set(
            " ".join(
                str(value)
                for value in (
                    fields.get("kind"),
                    " ".join(fields.get("tags") or []),
                )
                if value
            )
        )

    def _repo_scope_terms(self, fields: dict[str, Any]) -> set[str]:
        """Terms used to filter by repo-facing scope hints."""
        return _term_set(
            " ".join(
                str(value)
                for value in (
                    fields.get("title"),
                    fields.get("name"),
                    " ".join(fields.get("entity_refs") or []),
                    " ".join(fields.get("affects") or []),
                    " ".join((fields.get("links") or {}).get("depends_on") or []),
                    " ".join((fields.get("links") or {}).get("used_by") or []),
                )
                if value
            )
        )

    def _searchable_terms(self, fields: dict[str, Any]) -> set[str]:
        """Search terms used for the MVP ranking heuristic."""
        values: List[str] = []
        for value in (
            fields.get("kind"),
            fields.get("title"),
            fields.get("name"),
            fields.get("summary_short"),
            fields.get("summary_full"),
            fields.get("description"),
            fields.get("decision"),
            fields.get("rationale"),
            fields.get("task"),
            " ".join(fields.get("tags") or []),
            " ".join(fields.get("entity_refs") or []),
            " ".join(fields.get("affects") or []),
            " ".join(fields.get("new_facts") or []),
            " ".join(fields.get("changed_facts") or []),
            " ".join(fields.get("decisions") or []),
            " ".join(fields.get("open_questions") or []),
            " ".join(fields.get("next_actions") or []),
            " ".join((fields.get("links") or {}).get("depends_on") or []),
            " ".join((fields.get("links") or {}).get("used_by") or []),
        ):
            if value:
                values.append(str(value))
        return _term_set(" ".join(values))

    def _score_item(
        self,
        *,
        fields: dict[str, Any],
        item_type: str,
        task_terms: set[str],
        searchable_terms: set[str],
    ) -> float:
        """
        Score an item with simple, explainable heuristics.

        Priority is given to reusable rule/identity memory, then task-term
        overlap, then a modest trust bonus for approved/verified status.
        """
        relationship_bonus = self._relationship_score(fields, task_terms)
        return self.ranking_service.score_item(
            fields=fields,
            item_type=item_type,
            task_terms=task_terms,
            searchable_terms=searchable_terms,
            relationship_bonus=relationship_bonus,
        )

    def _relationship_score(self, fields: dict[str, Any], task_terms: set[str]) -> float:
        """
        Reward objects whose directly linked neighbors match the task.

        This is a lightweight Phase 6 heuristic. It does not replace global
        retrieval scoring, but it helps linked objects surface when nearby
        entities or decisions are clearly relevant to the current task.
        """
        object_id = str(fields.get("id") or "").strip()
        if not object_id or not task_terms:
            return 0

        bonus = 0.0
        for neighbor_info in self.linking_service.neighbors(object_id):
            neighbor = neighbor_info["neighbor"]
            if neighbor is None:
                continue

            neighbor_fields = vars(neighbor)
            neighbor_terms = self._searchable_terms(neighbor_fields)
            overlap = len(task_terms.intersection(neighbor_terms))
            if overlap:
                bonus += overlap * 6
            bonus += 2

        return bonus

    def _stable_identifier(self, item: Any) -> str:
        """Stable secondary sort key for deterministic results."""
        fields = vars(item)
        return str(fields.get("id") or fields.get("name") or "")

    @staticmethod
    def _sample_data() -> dict[str, list[Any]]:
        """
        Build a representative in-memory corpus for MVP smoke tests.

        The sample set includes active and inactive objects so callers can
        verify status filtering and simple ranking behavior.
        """
        return {
            "memory_entries": [
                MemoryEntry(
                    id="mem-rule-no-raw-history",
                    kind="rule",
                    title="No raw history in context",
                    summary_short=(
                        "Agent-facing context must be compiled from structured "
                        "memory instead of raw transcript history."
                    ),
                    status="approved",
                    tags=["rule", "context", "memory"],
                    source_refs=["ADR-0003"],
                ),
                MemoryEntry(
                    id="mem-rule-budget",
                    kind="rule",
                    title="Context must stay under budget",
                    summary_short=(
                        "Context packs must be compiled under an explicit token "
                        "budget before delivery to an agent."
                    ),
                    status="approved",
                    tags=["rule", "context", "budget"],
                    source_refs=["ADR-0004"],
                ),
                MemoryEntry(
                    id="mem-identity-canonical",
                    kind="identity",
                    title="Memory is canonical",
                    summary_short=(
                        "Structured memory is the authoritative shared context for "
                        "all agents in the system."
                    ),
                    status="approved",
                    tags=["identity", "memory"],
                    source_refs=["README.md", "AGENTS.md"],
                ),
                MemoryEntry(
                    id="mem-procedure-delta-writeback",
                    kind="procedure",
                    title="Session writeback is delta-based",
                    summary_short=(
                        "Session outcomes are written back as structured deltas "
                        "rather than full-history summaries."
                    ),
                    status="verified",
                    tags=["procedure", "writeback", "tool"],
                    source_refs=["ADR-0006"],
                ),
                MemoryEntry(
                    id="mem-archived-example",
                    kind="rule",
                    title="Archived example entry",
                    summary_short="This entry exists only to verify inactive filtering.",
                    status="archived",
                    tags=["rule"],
                    source_refs=["example"],
                ),
            ],
            "decisions": [
                Decision(
                    id="dec-context-budget",
                    kind="decision",
                    title="Compile under explicit token budget",
                    decision=(
                        "All agent-facing context must be selected and trimmed "
                        "under an explicit token budget."
                    ),
                    rationale="Prompt size control is a core system concern.",
                    status="approved",
                    affects=["context_compiler", "mcp"],
                    source_refs=["ADR-0004"],
                ),
                Decision(
                    id="dec-delta-writeback",
                    kind="decision",
                    title="Use session deltas for writeback",
                    decision=(
                        "Session outcomes must be written back as deltas with "
                        "new facts, changed facts, decisions, artifacts, open "
                        "questions, and next actions."
                    ),
                    rationale="This reduces duplication and retrieval noise.",
                    status="approved",
                    affects=["writeback", "sessions"],
                    source_refs=["ADR-0006"],
                ),
                Decision(
                    id="dec-superseded-example",
                    kind="decision",
                    title="Superseded decision example",
                    decision="This decision should be filtered during retrieval.",
                    status="superseded",
                    affects=["example"],
                    source_refs=["example"],
                ),
            ],
            "session_deltas": [
                SessionDelta(
                    id="delta-context-compiler-mvp",
                    session_id="session-context-compiler-mvp",
                    task="Implement context compiler MVP",
                    new_facts=[
                        "ContextCompiler produces schema-shaped context_pack output",
                    ],
                    decisions=[
                        "Budget enforcement happens during candidate selection",
                    ],
                    next_actions=[
                        "Wire adapters to request compiled context through MCP",
                    ],
                ),
                SessionDelta(
                    id="delta-adapter-skeletons",
                    session_id="session-adapter-skeletons",
                    task="Add Codex and Claude adapter scaffolds",
                    artifacts=[
                        "brain/adapters/codex_adapter.py",
                        "brain/adapters/claude_adapter.py",
                    ],
                    open_questions=[
                        "How should runtime-specific execution hooks be injected?",
                    ],
                    next_actions=[
                        "Replace adapter execution stubs with real model runtime calls",
                    ],
                ),
            ],
            "entities": [
                Entity(
                    id="entity-context-compiler",
                    kind="component",
                    name="context_compiler",
                    description=(
                        "Compiles compact task-specific context packs from memory "
                        "entries, decisions, entities, and session deltas."
                    ),
                    links={"depends_on": ["memory_api"], "used_by": ["mcp", "adapters"]},
                ),
                Entity(
                    id="entity-mcp",
                    kind="module",
                    name="mcp",
                    description=(
                        "Provides the canonical integration layer exposing memory "
                        "operations and context compilation to agents."
                    ),
                    links={"depends_on": ["context_compiler"], "used_by": ["codex", "claude"]},
                ),
            ],
        }


def _term_set(text: str) -> set[str]:
    """Normalize text into simple deterministic search terms for the MVP."""
    return {
        token.casefold()
        for token in re.findall(r"[A-Za-z0-9_./:-]+", str(text))
        if len(token) > 1
    }


__all__ = ["MemoryRetrievalBackend"]
