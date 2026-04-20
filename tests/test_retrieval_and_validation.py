"""Tests for retrieval ranking and context pack validation."""

import pytest

from brain.services.context_pack_validation import ContextPackValidator
from brain.services.retrieval import MemoryRetrievalBackend
from mcp.tools import MemoryTools


def test_memory_search_uses_global_backend_ranking() -> None:
    tools = MemoryTools(retrieval_backend=MemoryRetrievalBackend())

    results = tools.memory_search(
        query="budget context",
        k=3,
        types=["memory_entry", "decision"],
    )

    assert len(results) == 3
    assert results[0]["type"] in {"memory_entry", "decision"}
    assert any("budget" in str(result["title"]).lower() for result in results)


def test_retrieval_filters_inactive_and_respects_scope() -> None:
    retrieval = MemoryRetrievalBackend()

    entries = retrieval.get_memory_entries(
        task="memory rule filtering",
        memory_scope=["rule"],
    )

    assert entries
    assert all(entry.status != "archived" for entry in entries)
    assert all(entry.kind == "rule" or "rule" in entry.tags for entry in entries)


def test_context_pack_validator_rejects_invalid_limits() -> None:
    validator = ContextPackValidator()

    with pytest.raises(ValueError):
        validator.validate(
            {
                "id": "context_pack:test",
                "agent": "codex",
                "task": "invalid context pack",
                "rules_pack": [],
                "identity_pack": [],
                "knowledge_pack": [],
                "recent_pack": [],
                "tools_pack": [],
                "limits": {
                    "max_total_tokens": 100,
                    "max_output_tokens": 200,
                },
            }
        )


def test_written_session_delta_becomes_searchable() -> None:
    retrieval = MemoryRetrievalBackend()
    tools = MemoryTools(retrieval_backend=retrieval)

    delta_id = tools.session_delta_write(
        {
            "session_id": "searchable-delta-session",
            "task": "make delta searchable",
            "next_actions": ["verify retrieval after writeback"],
        }
    )

    results = tools.memory_search("searchable delta session", k=5, types=["session_delta"])

    assert any(result["id"] == delta_id for result in results)
