"""Importability and smoke tests for scaffolded app, prompt, and adapter assets."""

from pathlib import Path

from apps.compiler.main import CompilerApp
from apps.gateway.main import GatewayApp
from apps.gateway.mcp.bridge import build_mcp_capability_map
from apps.workers.compaction_worker import CompactionWorker
from apps.workers.graph_sync_worker import GraphSyncWorker
from apps.writeback.main import WritebackApp
from brain.api.memory_api import MemoryAPI


def test_gateway_and_compiler_scaffolds_are_importable() -> None:
    gateway = GatewayApp()
    compiler = CompilerApp(gateway.memory_api)

    health = gateway.health()
    compiled = compiler.compile_for_task(agent="codex", task="populate scaffold smoke test", budget_tokens=700)

    assert health["status"] == "ok"
    assert "context_pack" in compiled
    assert "runtime_payload" in compiled


def test_writeback_and_worker_scaffolds_are_importable() -> None:
    api = MemoryAPI()
    writeback = WritebackApp(api)
    compaction = CompactionWorker(api)
    graph = GraphSyncWorker(api)

    delta_id = writeback.submit_session_delta(
        {
            "session_id": "scaffold:test",
            "task": "verify scaffold writeback",
        }
    )
    compacted = compaction.run()
    traversal = graph.run(root_id="mem-rule-budget", depth=1)

    assert isinstance(delta_id, str)
    assert "tiers" in compacted
    assert "nodes" in traversal


def test_scaffold_files_exist() -> None:
    expected_paths = [
        Path("prompts/compiler/context_compile.md"),
        Path("prompts/summarizer/context_optimize.md"),
        Path("prompts/planner/scope_plan.md"),
        Path("prompts/validators/context_pack_validator.md"),
        Path("storage/docs/identity/project_identity.template.md"),
        Path("storage/docs/rules/global_rules.template.md"),
        Path("storage/docs/procedures/writeback_procedure.template.md"),
        Path("storage/docs/decisions/decision_record.template.json"),
        Path("storage/docs/entities/entity_record.template.json"),
        Path("storage/docs/sessions/session_delta.template.json"),
        Path("adapters/codex/config.template.toml"),
        Path("adapters/codex/instructions.md"),
        Path("adapters/claude/CLAUDE.template.md"),
        Path("adapters/claude/skills/memory_workflow.md"),
        Path("adapters/generic/client_examples/python_client.py"),
    ]

    missing = [str(path) for path in expected_paths if not path.exists()]
    assert not missing


def test_gateway_mcp_bridge_reports_capabilities() -> None:
    capability_map = build_mcp_capability_map(GatewayApp().memory_tools)
    assert "context_compile" in capability_map
    assert "memory_snapshot_export" in capability_map
