"""Tests for the canonical memory API facade."""

from brain.api.memory_api import MemoryAPI
from brain.services.retrieval import MemoryRetrievalBackend
from mcp.tools import MemoryTools


def test_memory_api_can_link_existing_objects() -> None:
    retrieval_backend = MemoryRetrievalBackend()
    api = MemoryAPI(retrieval_backend=retrieval_backend)

    result = api.link_memory("mem-rule-budget", "entity-context-compiler", "supports")

    assert result is True
    links = api.get_links_for_id("mem-rule-budget")
    assert len(links) == 1
    assert links[0]["target_id"] == "entity-context-compiler"
    assert links[0]["link_type"] == "supports"


def test_memory_api_write_and_search_memory_entry() -> None:
    retrieval_backend = MemoryRetrievalBackend()
    api = MemoryAPI(retrieval_backend=retrieval_backend)

    memory_id = api.write_memory_entry(
        {
            "kind": "rule",
            "title": "Always register durable decisions",
            "summary_short": "Decisions should be written separately from session deltas.",
            "status": "approved",
            "tags": ["rule", "decision"],
            "source_refs": ["ADR-0006"],
        }
    )

    results = api.search_memory(query="durable decisions", k=5, types=["memory_entry"])

    assert any(result["id"] == memory_id for result in results)


def test_memory_api_compile_context_returns_valid_pack() -> None:
    api = MemoryAPI(retrieval_backend=MemoryRetrievalBackend())

    context_pack = api.compile_context(
        agent="generic",
        task="prepare context pack through memory api",
        budget_tokens=750,
        memory_scope=["rule", "identity"],
    )

    assert context_pack["agent"] == "generic"
    assert context_pack["limits"]["max_total_tokens"] == 750
    assert isinstance(context_pack["rules_pack"], list)


def test_mcp_memory_link_round_trip_uses_canonical_api() -> None:
    retrieval_backend = MemoryRetrievalBackend()
    tools = MemoryTools(retrieval_backend=retrieval_backend)

    memory_id = tools.memory_write(
        {
            "kind": "rule",
            "title": "Keep links canonical",
            "summary_short": "Links should be created through the canonical memory API path.",
            "status": "approved",
        }
    )

    assert tools.memory_link(memory_id, "entity-mcp", "supports") is True

    api = tools.memory_api
    links = api.get_links_for_id(memory_id)
    assert len(links) == 1
    assert links[0]["target_id"] == "entity-mcp"
