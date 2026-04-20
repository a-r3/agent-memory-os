"""Smoke tests for future Phase 11+ scaffolds."""

from pathlib import Path

from apps.compiler.compressors.cache_friendly_compressor import CacheFriendlyCompressor
from apps.compiler.packers.runtime_payload_packer import RuntimePayloadPacker
from apps.compiler.planners.cache_refresh_planner import CacheRefreshPlanner
from apps.compiler.planners.coordination_plan import CoordinationPlanner
from apps.gateway.main import GatewayApp
from apps.gateway.mcp.runtime_bridge import build_runtime_capability_map
from apps.gateway.routes.operations import operations_report_route
from apps.gateway.routes.runtime import runtime_payload_route
from apps.gateway.routes.storage import snapshot_list_route
from apps.workers.policy_audit_worker import PolicyAuditWorker
from apps.workers.recovery_worker import RecoveryWorker
from apps.workers.reporting_worker import ReportingWorker
from apps.workers.session_coordination_worker import SessionCoordinationWorker
from apps.writeback.approval import ApprovalPlanner
from apps.writeback.archive import ArchivePlanner
from brain.api.memory_api import MemoryAPI


def test_future_routes_and_workers_are_importable() -> None:
    gateway = GatewayApp()
    api = gateway.memory_api

    runtime_payload = runtime_payload_route(gateway, agent="codex", task="future runtime route test", budget_tokens=750)
    ops_report = operations_report_route(gateway)
    snapshot_list = snapshot_list_route(gateway)
    cache_plan = CacheRefreshPlanner(api).plan(task="future cache planning", agent="codex")
    coordination = CoordinationPlanner(api).plan(task="future coordination", agents=["codex", "claude"])
    archive_plan = ArchivePlanner(api).build_archive_plan()
    approval = ApprovalPlanner(api).evaluate(payload_type="memory_entry", payload={"kind": "rule", "title": "x", "summary_short": "y", "status": "draft"})
    policy_audit = PolicyAuditWorker(api).run()
    reporting = ReportingWorker(api).run()
    session_coordination = SessionCoordinationWorker(api).run(task="future worker coordination", agents=["codex", "claude"])

    assert "runtime_payload" in runtime_payload
    assert "health" in ops_report
    assert isinstance(snapshot_list, list)
    assert "should_refresh_stable_context" in cache_plan
    assert coordination["handoff_required"] is True
    assert "cold_count" in archive_plan
    assert "requires_approval" in approval
    assert "trust" in policy_audit
    assert "snapshots" in reporting
    assert session_coordination["handoff_required"] is True


def test_future_packers_and_compressors_are_importable() -> None:
    api = MemoryAPI()
    context_pack = api.compile_context(agent="codex", task="future packer test", budget_tokens=800)

    runtime_packer = RuntimePayloadPacker(api).pack(agent="codex", task="future packer test", context_pack=context_pack)
    compressor = CacheFriendlyCompressor(api).compress(context_pack=context_pack, max_total_tokens=500)
    recovery_worker = RecoveryWorker(api)

    assert "runtime_payload" in runtime_packer
    assert "context_pack" in compressor
    assert recovery_worker is not None


def test_future_phase_templates_exist() -> None:
    expected_paths = [
        Path("docs/phase11_plus_plan.md"),
        Path("prompts/compiler/runtime_payload.md"),
        Path("prompts/planner/cache_refresh_plan.md"),
        Path("prompts/planner/coordination_plan.md"),
        Path("prompts/validators/snapshot_integrity.md"),
        Path("prompts/validators/policy_gate.md"),
        Path("prompts/validators/operations_review.md"),
        Path("storage/snapshots/snapshot_manifest.template.json"),
        Path("storage/exports/export_manifest.template.json"),
        Path("storage/exports/operations_report.template.json"),
        Path("storage/archives/archive_manifest.template.json"),
        Path("storage/archives/recovery_notes.template.md"),
        Path("storage/docs/sessions/session_handoff.template.json"),
        Path("storage/docs/rules/policy_gate.template.md"),
        Path("adapters/codex/runtime.template.md"),
        Path("adapters/codex/policy.template.toml"),
        Path("adapters/claude/skills/runtime_payload_review.md"),
        Path("adapters/generic/client_examples/runtime_client.py"),
        Path("adapters/generic/client_examples/handoff_client.py"),
        Path("adapters/generic/client_examples/ops_client.py"),
    ]
    assert all(path.exists() for path in expected_paths)


def test_runtime_bridge_reports_future_capabilities() -> None:
    capability_map = build_runtime_capability_map(GatewayApp().memory_tools)
    assert "runtime_payload_preview" in capability_map
    assert "memory_trust_report" in capability_map
