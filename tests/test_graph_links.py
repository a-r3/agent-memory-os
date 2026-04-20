"""Smoke tests for link traversal and relationship-aware graph surfaces."""

from apps.workers.graph_sync_worker import GraphSyncWorker
from brain.api.entities import EntitiesAPI
from brain.api.memory_api import MemoryAPI


def test_graph_sync_worker_returns_nodes_and_edges() -> None:
    result = GraphSyncWorker(MemoryAPI()).run(root_id="mem-rule-budget", depth=1)
    assert "nodes" in result
    assert "edges" in result


def test_entities_api_lists_normalized_entities() -> None:
    entities = EntitiesAPI(MemoryAPI()).list()
    assert isinstance(entities, list)
