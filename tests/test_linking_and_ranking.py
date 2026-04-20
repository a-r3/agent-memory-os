"""Direct tests for Phase 6 linking and ranking services."""

from brain.services.linking import LinkingService
from brain.services.ranking import RetrievalRankingService
from brain.services.retrieval import MemoryRetrievalBackend


def test_linking_service_neighbors_returns_connected_object() -> None:
    retrieval = MemoryRetrievalBackend()
    retrieval.links.append(
        {
            "id": "link:test",
            "source_id": "mem-rule-budget",
            "target_id": "entity-mcp",
            "link_type": "supports",
        }
    )

    neighbors = LinkingService(retrieval).neighbors("mem-rule-budget")

    assert len(neighbors) == 1
    assert neighbors[0]["neighbor_id"] == "entity-mcp"
    assert neighbors[0]["neighbor"] is not None


def test_ranking_service_rewards_relationship_bonus() -> None:
    ranking = RetrievalRankingService()
    fields = {
        "id": "mem-rule-budget",
        "kind": "rule",
        "tags": ["rule", "context"],
        "status": "approved",
    }

    without_relationship = ranking.score_item(
        fields=fields,
        item_type="memory_entry",
        task_terms={"mcp", "integration"},
        searchable_terms={"budget", "context"},
        relationship_bonus=0,
    )
    with_relationship = ranking.score_item(
        fields=fields,
        item_type="memory_entry",
        task_terms={"mcp", "integration"},
        searchable_terms={"budget", "context"},
        relationship_bonus=12,
    )

    assert with_relationship > without_relationship
