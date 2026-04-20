"""Tests for Phase 9 optimization and Phase 10 operational readiness services."""

from pathlib import Path

from brain.adapters.codex_adapter import CodexAdapter
from brain.api.memory_api import MemoryAPI
from brain.services.persistence import PersistenceService
from brain.services.retrieval import MemoryRetrievalBackend
from brain.services.summarization import SummarizationService
from mcp.tools import MemoryTools


def test_context_optimize_preserves_schema_and_reduces_budget() -> None:
    tools = MemoryTools(retrieval_backend=MemoryRetrievalBackend())
    summarizer = SummarizationService()

    context_pack = {
        "id": "context_pack:test-optimize",
        "agent": "codex",
        "task": "optimize this context pack",
        "rules_pack": ["Rule " * 80],
        "identity_pack": ["Identity " * 60],
        "knowledge_pack": ["Knowledge " * 120],
        "recent_pack": ["Recent " * 80],
        "tools_pack": ["Tools " * 80],
        "limits": {
            "max_total_tokens": 1200,
            "max_output_tokens": 300,
        },
    }

    optimized = tools.context_optimize(context_pack, max_total_tokens=500)

    optimized_input_tokens = summarizer._estimate_pack_tokens(optimized)
    assert optimized["limits"]["max_total_tokens"] == 500
    assert optimized_input_tokens <= 200


def test_memory_snapshot_export_and_import_round_trip(tmp_path: Path) -> None:
    retrieval = MemoryRetrievalBackend()
    api = MemoryAPI(
        retrieval_backend=retrieval,
        persistence_service=PersistenceService(base_dir=tmp_path),
    )

    written_id = api.write_memory_entry(
        {
            "kind": "rule",
            "title": "Snapshot export rule",
            "summary_short": "Snapshots should round-trip through persistence service.",
            "status": "approved",
            "source_refs": ["operations"],
        }
    )
    export_result = api.export_snapshot(label="roundtrip")

    fresh_retrieval = MemoryRetrievalBackend(memory_entries=[], decisions=[], session_deltas=[], entities=[], links=[])
    fresh_api = MemoryAPI(
        retrieval_backend=fresh_retrieval,
        persistence_service=PersistenceService(base_dir=tmp_path),
    )
    import_result = fresh_api.import_snapshot(snapshot_path=export_result["path"], merge=True)

    ids = {item["id"] for item in fresh_api.list_objects(types=["memory_entry"])}
    assert written_id in ids
    assert import_result["counts"]["memory_entries"] >= 1


def test_mcp_tier_report_and_runtime_payload_preview() -> None:
    tools = MemoryTools(retrieval_backend=MemoryRetrievalBackend())
    context_pack = tools.context_compile(
        agent="codex",
        task="prepare stable runtime payload",
        budget_tokens=800,
    )

    tier_report = tools.memory_tier_report()
    runtime_payload = tools.runtime_payload_preview("codex", "prepare stable runtime payload", context_pack)

    assert "hot" in tier_report["counts"]
    assert runtime_payload["agent"] == "codex"
    assert runtime_payload["sections"]
    assert isinstance(runtime_payload["cache_key"], str)


def test_adapter_exposes_runtime_payload_preview() -> None:
    tools = MemoryTools(retrieval_backend=MemoryRetrievalBackend())
    result = CodexAdapter(memory_tools=tools).execute_task("runtime payload adapter test", "adapter-runtime")

    assert "runtime_payload" in result
    assert result["runtime_payload"]["agent"] == "codex"
