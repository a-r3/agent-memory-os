"""Tests for Phase 6 relationship services and Phase 7 hygiene services."""

from brain.api.memory_api import MemoryAPI
from brain.services.memory_hygiene import MemoryHygieneService
from brain.services.relationship_traversal import RelationshipTraversalService
from brain.services.retrieval import MemoryRetrievalBackend


def test_relationship_traversal_returns_linked_neighbors() -> None:
    api = MemoryAPI(retrieval_backend=MemoryRetrievalBackend())
    api.link_memory("mem-rule-budget", "entity-mcp", "supports")

    traversal = RelationshipTraversalService(api).traverse(
        root_id="mem-rule-budget",
        depth=1,
    )

    node_ids = {node["id"] for node in traversal["nodes"]}
    assert "mem-rule-budget" in node_ids
    assert "entity-mcp" in node_ids
    assert traversal["edges"][0]["link_type"] == "supports"


def test_link_aware_search_promotes_linked_memory_entry() -> None:
    api = MemoryAPI(retrieval_backend=MemoryRetrievalBackend())
    memory_id = api.write_memory_entry(
        {
            "kind": "rule",
            "title": "Gateway discipline",
            "summary_short": "Adapters stay thin and do not talk to storage directly.",
            "status": "approved",
        }
    )
    api.link_memory(memory_id, "entity-mcp", "supports")

    results = api.search_memory(
        query="mcp integration layer",
        k=3,
        types=["memory_entry"],
    )

    assert results
    assert results[0]["id"] == memory_id


def test_memory_hygiene_reports_promotions_and_invalid_links() -> None:
    retrieval_backend = MemoryRetrievalBackend()
    api = MemoryAPI(retrieval_backend=retrieval_backend)
    hygiene = MemoryHygieneService(api)

    api.write_session_delta(
        {
            "session_id": "session-one",
            "task": "record repeated fact one",
            "new_facts": ["Register durable decisions separately."],
        }
    )
    api.write_session_delta(
        {
            "session_id": "session-two",
            "task": "record repeated fact two",
            "new_facts": ["Register durable decisions separately."],
        }
    )

    retrieval_backend.links.append(
        {
            "id": "link:invalid",
            "source_id": "missing-source",
            "target_id": "entity-mcp",
            "link_type": "supports",
        }
    )

    promotions = hygiene.suggest_promotions()
    link_validation = hygiene.validate_links()
    report = hygiene.generate_health_report()

    assert promotions
    assert promotions[0]["suggested_action"] == "promote_to_memory_entry"
    assert link_validation["is_valid"] is False
    assert report["promotion_candidate_groups"] >= 1
    assert report["link_validation"]["missing_links"]
