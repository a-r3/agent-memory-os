"""
Minimal Context Compiler MVP for Agent Memory OS.

This module turns structured memory objects into a compact ``context_pack``
payload that matches ``schemas/context_pack.schema.json``.

Design constraints for the MVP:

- operate on existing Python model classes without introducing a new runtime
  dependency
- avoid raw transcript injection by using structured summaries only
- enforce an explicit token budget with deterministic selection and trimming
- keep integration simple so ``mcp/tools.py::MemoryTools.context_compile`` can
  delegate to this compiler later
"""

from __future__ import annotations

from dataclasses import dataclass, field
from math import ceil
import re
from typing import Any, Callable, Dict, Iterable, List, Mapping, Optional, Sequence
from uuid import uuid4

from brain.models.decision import Decision
from brain.models.entity import Entity
from brain.models.memory_entry import MemoryEntry
from brain.models.session_delta import SessionDelta


SUPPORTED_PACKS = (
    "rules_pack",
    "identity_pack",
    "knowledge_pack",
    "recent_pack",
    "tools_pack",
)

PACK_PRIORITY = {
    "rules_pack": 0,
    "identity_pack": 1,
    "knowledge_pack": 2,
    "recent_pack": 3,
    "tools_pack": 4,
}

STATUS_WEIGHT = {
    "approved": 30,
    "verified": 20,
    "unverified": 8,
    "draft": 2,
    "pending": 2,
    "archived": -100,
    "superseded": -100,
}


@dataclass(frozen=True)
class ContextCompilerConfig:
    """Configuration knobs for the minimal compiler."""

    reserved_output_ratio: float = 0.35
    minimum_output_tokens: int = 256
    minimum_input_tokens: int = 128
    max_items_per_pack: int = 8


@dataclass
class ContextCandidate:
    """Internal normalized representation used during ranking and selection."""

    pack_name: str
    text: str
    score: float
    token_count: int
    source_id: str
    source_kind: str
    status: str = "unverified"
    tags: List[str] = field(default_factory=list)


class ContextCompiler:
    """
    Compile a task-specific context pack from memory model objects.

    The compiler accepts in-memory objects and returns a plain dictionary that
    conforms to ``schemas/context_pack.schema.json``.
    """

    def __init__(
        self,
        config: Optional[ContextCompilerConfig] = None,
        token_estimator: Optional[Callable[[str], int]] = None,
    ) -> None:
        self.config = config or ContextCompilerConfig()
        self.token_estimator = token_estimator or estimate_tokens

    def compile_context_pack(
        self,
        *,
        agent: str,
        task: str,
        budget_tokens: int,
        memory_entries: Sequence[MemoryEntry | Mapping[str, Any]] | None = None,
        decisions: Sequence[Decision | Mapping[str, Any]] | None = None,
        session_deltas: Sequence[SessionDelta | Mapping[str, Any]] | None = None,
        entities: Sequence[Entity | Mapping[str, Any]] | None = None,
        memory_scope: Optional[Sequence[str]] = None,
        repo_scope: Optional[Sequence[str]] = None,
        max_output_tokens: Optional[int] = None,
        priority_ids: Optional[Sequence[str]] = None,
    ) -> Dict[str, Any]:
        """
        Build a compact ``context_pack`` within a strict token budget.

        ``memory_scope`` is treated as a lightweight allow-list for entry kinds
        or tags. ``repo_scope`` is treated as a lightweight allow-list for
        entity references, affected modules, or entity names.
        """

        if not agent.strip():
            raise ValueError("agent must be a non-empty string")
        if not task.strip():
            raise ValueError("task must be a non-empty string")
        if budget_tokens <= 0:
            raise ValueError("budget_tokens must be positive")

        resolved_max_output_tokens = self._resolve_max_output_tokens(
            budget_tokens=budget_tokens,
            requested=max_output_tokens,
        )
        available_input_tokens = max(
            self.config.minimum_input_tokens,
            budget_tokens - resolved_max_output_tokens,
        )

        scoped_memory_entries = self._apply_scope_filters(
            items=memory_entries or [],
            memory_scope=memory_scope,
            repo_scope=repo_scope,
        )
        scoped_decisions = self._apply_scope_filters(
            items=decisions or [],
            memory_scope=memory_scope,
            repo_scope=repo_scope,
        )
        scoped_session_deltas = self._apply_scope_filters(
            items=session_deltas or [],
            memory_scope=memory_scope,
            repo_scope=repo_scope,
        )
        scoped_entities = self._apply_scope_filters(
            items=entities or [],
            memory_scope=memory_scope,
            repo_scope=repo_scope,
        )

        candidates = self._build_candidates(
            task=task,
            memory_entries=scoped_memory_entries,
            decisions=scoped_decisions,
            session_deltas=scoped_session_deltas,
            entities=scoped_entities,
            priority_ids=priority_ids,
        )
        selected = self._select_candidates(
            candidates=candidates,
            budget_tokens=available_input_tokens,
        )

        context_pack = {
            "id": f"context_pack:{uuid4()}",
            "agent": agent,
            "task": task,
            "rules_pack": [],
            "identity_pack": [],
            "knowledge_pack": [],
            "recent_pack": [],
            "tools_pack": [],
            "limits": {
                "max_total_tokens": budget_tokens,
                "max_output_tokens": resolved_max_output_tokens,
            },
        }

        for candidate in selected:
            context_pack[candidate.pack_name].append(candidate.text)

        return context_pack

    def _resolve_max_output_tokens(
        self,
        *,
        budget_tokens: int,
        requested: Optional[int],
    ) -> int:
        if requested is not None:
            if requested <= 0:
                raise ValueError("max_output_tokens must be positive when provided")
            return min(requested, budget_tokens)

        derived = int(budget_tokens * self.config.reserved_output_ratio)
        return max(self.config.minimum_output_tokens, min(derived, budget_tokens))

    def _apply_scope_filters(
        self,
        *,
        items: Sequence[Any],
        memory_scope: Optional[Sequence[str]],
        repo_scope: Optional[Sequence[str]],
    ) -> List[Any]:
        if not memory_scope and not repo_scope:
            return list(items)

        memory_scope_set = {item.casefold() for item in (memory_scope or [])}
        repo_scope_set = {item.casefold() for item in (repo_scope or [])}
        filtered: List[Any] = []

        for item in items:
            fields = _object_fields(item)

            memory_fields = set()
            for value in (
                fields.get("kind"),
                *(fields.get("tags") or []),
            ):
                if isinstance(value, str):
                    memory_fields.add(value.casefold())

            repo_fields = set()
            for value in (
                *(fields.get("entity_refs") or []),
                *(fields.get("affects") or []),
                fields.get("name"),
                fields.get("title"),
            ):
                if isinstance(value, str):
                    repo_fields.add(value.casefold())

            memory_match = not memory_scope_set or bool(memory_fields & memory_scope_set)
            repo_match = not repo_scope_set or bool(repo_fields & repo_scope_set)
            if memory_match and repo_match:
                filtered.append(item)

        return filtered

    def _build_candidates(
        self,
        *,
        task: str,
        memory_entries: Sequence[Any],
        decisions: Sequence[Any],
        session_deltas: Sequence[Any],
        entities: Sequence[Any],
        priority_ids: Optional[Sequence[str]],
    ) -> List[ContextCandidate]:
        task_terms = _normalized_terms(task)
        priority_id_set = {value.strip() for value in (priority_ids or []) if isinstance(value, str) and value.strip()}
        candidates: List[ContextCandidate] = []

        for entry in memory_entries:
            candidate = self._memory_entry_candidate(entry, task_terms, priority_id_set)
            if candidate is not None:
                candidates.append(candidate)

        for decision in decisions:
            candidate = self._decision_candidate(decision, task_terms, priority_id_set)
            if candidate is not None:
                candidates.append(candidate)

        for delta in session_deltas:
            candidate = self._session_delta_candidate(delta, task_terms, priority_id_set)
            if candidate is not None:
                candidates.append(candidate)

        for entity in entities:
            candidate = self._entity_candidate(entity, task_terms, priority_id_set)
            if candidate is not None:
                candidates.append(candidate)

        return candidates

    def _memory_entry_candidate(
        self,
        entry: MemoryEntry | Mapping[str, Any],
        task_terms: set[str],
        priority_ids: set[str],
    ) -> Optional[ContextCandidate]:
        fields = _object_fields(entry)
        status = str(fields.get("status") or "unverified")
        if not _is_active_status(status):
            return None

        pack_name = _pack_for_memory_entry(fields)
        text = _render_memory_entry(fields)
        return self._make_candidate(
            pack_name=pack_name,
            text=text,
            task_terms=task_terms,
            priority_ids=priority_ids,
            status=status,
            source_id=str(fields.get("id") or ""),
            source_kind=str(fields.get("kind") or "memory_entry"),
            tags=list(fields.get("tags") or []),
        )

    def _decision_candidate(
        self,
        decision: Decision | Mapping[str, Any],
        task_terms: set[str],
        priority_ids: set[str],
    ) -> Optional[ContextCandidate]:
        fields = _object_fields(decision)
        status = str(fields.get("status") or "approved")
        if not _is_active_status(status):
            return None

        text = _render_decision(fields)
        return self._make_candidate(
            pack_name="knowledge_pack",
            text=text,
            task_terms=task_terms,
            priority_ids=priority_ids,
            status=status,
            source_id=str(fields.get("id") or ""),
            source_kind=str(fields.get("kind") or "decision"),
            tags=[],
        )

    def _session_delta_candidate(
        self,
        delta: SessionDelta | Mapping[str, Any],
        task_terms: set[str],
        priority_ids: set[str],
    ) -> Optional[ContextCandidate]:
        fields = _object_fields(delta)
        text = _render_session_delta(fields)
        if not text:
            return None

        return self._make_candidate(
            pack_name="recent_pack",
            text=text,
            task_terms=task_terms,
            priority_ids=priority_ids,
            status="unverified",
            source_id=str(fields.get("id") or ""),
            source_kind="session_delta",
            tags=[],
        )

    def _entity_candidate(
        self,
        entity: Entity | Mapping[str, Any],
        task_terms: set[str],
        priority_ids: set[str],
    ) -> Optional[ContextCandidate]:
        fields = _object_fields(entity)
        text = _render_entity(fields)
        if not text:
            return None

        return self._make_candidate(
            pack_name="knowledge_pack",
            text=text,
            task_terms=task_terms,
            priority_ids=priority_ids,
            status="verified",
            source_id=str(fields.get("id") or ""),
            source_kind=str(fields.get("kind") or "entity"),
            tags=[],
        )

    def _make_candidate(
        self,
        *,
        pack_name: str,
        text: str,
        task_terms: set[str],
        priority_ids: set[str],
        status: str,
        source_id: str,
        source_kind: str,
        tags: List[str],
    ) -> Optional[ContextCandidate]:
        if not text.strip():
            return None

        token_count = self.token_estimator(text)
        score = self._score_candidate(
            pack_name=pack_name,
            text=text,
            task_terms=task_terms,
            priority_ids=priority_ids,
            status=status,
            tags=tags,
            source_id=source_id,
        )

        return ContextCandidate(
            pack_name=pack_name,
            text=text,
            score=score,
            token_count=token_count,
            source_id=source_id,
            source_kind=source_kind,
            status=status,
            tags=tags,
        )

    def _score_candidate(
        self,
        *,
        pack_name: str,
        text: str,
        task_terms: set[str],
        priority_ids: set[str],
        status: str,
        tags: Sequence[str],
        source_id: str,
    ) -> float:
        normalized_text = _normalized_terms(text)
        overlap_score = len(task_terms & normalized_text) * 10
        tag_overlap_score = len(task_terms & {tag.casefold() for tag in tags}) * 6
        status_score = STATUS_WEIGHT.get(status.casefold(), 0)
        pack_score = (len(SUPPORTED_PACKS) - PACK_PRIORITY[pack_name]) * 4
        brevity_bonus = max(0, 24 - min(self.token_estimator(text), 24))
        priority_bonus = 18 if source_id in priority_ids else 0
        return overlap_score + tag_overlap_score + status_score + pack_score + brevity_bonus + priority_bonus

    def _select_candidates(
        self,
        *,
        candidates: Sequence[ContextCandidate],
        budget_tokens: int,
    ) -> List[ContextCandidate]:
        if budget_tokens <= 0:
            return []

        selected: List[ContextCandidate] = []
        remaining_budget = budget_tokens
        per_pack_counts = {pack_name: 0 for pack_name in SUPPORTED_PACKS}

        ordered = sorted(
            candidates,
            key=lambda candidate: (
                PACK_PRIORITY[candidate.pack_name],
                -candidate.score,
                candidate.token_count,
                candidate.source_id,
            ),
        )

        for candidate in ordered:
            if per_pack_counts[candidate.pack_name] >= self.config.max_items_per_pack:
                continue

            item = candidate
            if item.token_count > remaining_budget:
                trimmed_text = trim_text_to_token_budget(
                    item.text,
                    remaining_budget,
                    estimator=self.token_estimator,
                )
                trimmed_tokens = self.token_estimator(trimmed_text)
                if not trimmed_text or trimmed_tokens <= 0:
                    continue
                item = ContextCandidate(
                    pack_name=item.pack_name,
                    text=trimmed_text,
                    score=item.score,
                    token_count=trimmed_tokens,
                    source_id=item.source_id,
                    source_kind=item.source_kind,
                    status=item.status,
                    tags=item.tags,
                )

            if item.token_count > remaining_budget:
                continue

            selected.append(item)
            remaining_budget -= item.token_count
            per_pack_counts[item.pack_name] += 1
            if remaining_budget <= 0:
                break

        return selected


def estimate_tokens(text: str) -> int:
    """
    Approximate token usage without external tokenizer dependencies.

    The heuristic is intentionally conservative and stable. For English-centric
    text it tracks reasonably well with the common ``~4 characters per token``
    rule while still accounting for short punctuation-heavy strings.
    """

    if not text:
        return 0

    compact = re.sub(r"\s+", " ", text.strip())
    if not compact:
        return 0

    return max(1, ceil(len(compact) / 4))


def trim_text_to_token_budget(
    text: str,
    budget_tokens: int,
    *,
    estimator: Callable[[str], int] = estimate_tokens,
) -> str:
    """Trim text deterministically so it fits into ``budget_tokens``."""

    if budget_tokens <= 0:
        return ""
    if estimator(text) <= budget_tokens:
        return text

    words = text.split()
    if not words:
        return ""

    trimmed_words: List[str] = []
    for word in words:
        candidate = " ".join([*trimmed_words, word]).strip()
        suffix = " ..."
        if estimator(candidate + suffix) > budget_tokens:
            break
        trimmed_words.append(word)

    if not trimmed_words:
        return ""

    return " ".join(trimmed_words).strip() + " ..."


def _object_fields(item: Any) -> Dict[str, Any]:
    if isinstance(item, Mapping):
        return dict(item)
    return vars(item)


def _normalized_terms(text: str) -> set[str]:
    return {
        token.casefold()
        for token in re.findall(r"[A-Za-z0-9_./:-]+", text)
        if len(token) > 1
    }


def _is_active_status(status: str) -> bool:
    return status.casefold() not in {"archived", "superseded"}


def _pack_for_memory_entry(fields: Mapping[str, Any]) -> str:
    kind = str(fields.get("kind") or "").casefold()
    tags = {tag.casefold() for tag in (fields.get("tags") or []) if isinstance(tag, str)}

    if kind in {"rule", "rules", "policy", "constraint"} or "rule" in tags:
        return "rules_pack"
    if kind in {"identity", "preference", "project_identity"} or "identity" in tags:
        return "identity_pack"
    if kind in {"tool", "workflow", "procedure", "playbook"} or "tool" in tags:
        return "tools_pack"
    if kind in {"session", "recent", "event"} or "recent" in tags:
        return "recent_pack"
    return "knowledge_pack"


def _render_memory_entry(fields: Mapping[str, Any]) -> str:
    title = str(fields.get("title") or fields.get("id") or "memory_entry")
    summary = str(fields.get("summary_short") or fields.get("summary_full") or "").strip()
    status = str(fields.get("status") or "unverified")
    tags = ", ".join(fields.get("tags") or [])
    sources = ", ".join(fields.get("source_refs") or [])
    confidence = fields.get("confidence")

    lines = [f"{title} [{status}]"]
    if summary:
        lines.append(summary)
    if tags:
        lines.append(f"Tags: {tags}")
    if confidence is not None:
        lines.append(f"Confidence: {confidence}")
    if sources:
        lines.append(f"Sources: {sources}")
    return " | ".join(lines)


def _render_decision(fields: Mapping[str, Any]) -> str:
    title = str(fields.get("title") or fields.get("id") or "decision")
    decision_text = str(fields.get("decision") or "").strip()
    rationale = str(fields.get("rationale") or "").strip()
    status = str(fields.get("status") or "approved")
    affects = ", ".join(fields.get("affects") or [])
    owner = str(fields.get("owner") or "").strip()
    sources = ", ".join(fields.get("source_refs") or [])

    lines = [f"Decision: {title} [{status}]"]
    if decision_text:
        lines.append(decision_text)
    if rationale:
        lines.append(f"Rationale: {rationale}")
    if affects:
        lines.append(f"Affects: {affects}")
    if owner:
        lines.append(f"Owner: {owner}")
    if sources:
        lines.append(f"Sources: {sources}")
    return " | ".join(lines)


def _render_session_delta(fields: Mapping[str, Any]) -> str:
    task = str(fields.get("task") or fields.get("session_id") or "recent session")
    components: List[str] = [f"Recent session: {task}"]

    for label, key in (
        ("New facts", "new_facts"),
        ("Changed facts", "changed_facts"),
        ("Decisions", "decisions"),
        ("Artifacts", "artifacts"),
        ("Open questions", "open_questions"),
        ("Next actions", "next_actions"),
    ):
        values = fields.get(key) or []
        if values:
            components.append(f"{label}: {', '.join(values)}")

    if len(components) == 1:
        return ""
    return " | ".join(components)


def _render_entity(fields: Mapping[str, Any]) -> str:
    name = str(fields.get("name") or fields.get("id") or "entity")
    kind = str(fields.get("kind") or "entity")
    description = str(fields.get("description") or "").strip()
    links = fields.get("links") or {}
    depends_on = ", ".join(links.get("depends_on") or [])
    used_by = ", ".join(links.get("used_by") or [])

    lines = [f"Entity: {name} [{kind}]"]
    if description:
        lines.append(description)
    if depends_on:
        lines.append(f"Depends on: {depends_on}")
    if used_by:
        lines.append(f"Used by: {used_by}")
    return " | ".join(lines)
