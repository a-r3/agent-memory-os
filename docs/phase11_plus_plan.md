# Agent Memory OS — Future Phase Plan

This document extends the current roadmap beyond Phase 10 without changing the
canonical architecture or existing module placements.

The intent is to define the next sequence of work after:

- Phase 9: cost and performance optimization
- Phase 10: operational readiness

These future phases stay consistent with the architecture rule that memory
remains canonical, adapters remain thin, and MCP remains the integration
surface.

## Phase 11 — Persistent Storage and Replay

### Goal
Move from in-memory-only execution to durable storage orchestration and replay.

### Modules
- `apps/gateway/routes/storage.py`
  - snapshot/export/archive route helpers
  - delegates through `mcp/tools.py`
- `apps/compiler/planners/cache_refresh_planner.py`
  - determines when stable prompt sections should be recomputed
- `apps/writeback/archive.py`
  - plans archival actions using canonical hygiene signals
- `apps/workers/recovery_worker.py`
  - imports snapshots and reports replay results
- `prompts/planner/cache_refresh_plan.md`
  - prompt template for persistence and cache refresh planning
- `prompts/validators/snapshot_integrity.md`
  - prompt template for snapshot integrity verification
- `storage/snapshots/snapshot_manifest.template.json`
  - structured manifest for snapshot metadata
- `storage/exports/export_manifest.template.json`
  - structured export metadata
- `storage/archives/archive_manifest.template.json`
  - archival metadata and provenance

### Integration Notes
- All persistence actions must continue to flow through `brain/api/memory_api.py`.
- Snapshot import/export remains separate from canonical `context_pack`.
- Trust checks apply before replaying imported content into active memory.

### Minimal Tests
- importability of recovery worker and archive planner
- snapshot route smoke test
- manifest template existence check

## Phase 12 — Runtime Connectors and Execution Handoff

### Goal
Bridge compiled context into real provider runtimes without moving execution
logic into adapters themselves.

### Modules
- `apps/gateway/routes/runtime.py`
  - runtime payload preview and execution-hand-off route helpers
- `apps/gateway/mcp/runtime_bridge.py`
  - stable mapping of runtime-related MCP capabilities
- `apps/compiler/packers/runtime_payload_packer.py`
  - assembles transport-neutral runtime payloads from `context_pack`
- `prompts/compiler/runtime_payload.md`
  - prompt template describing stable runtime payload structure
- `adapters/codex/runtime.template.md`
  - provider-facing runtime contract guidance
- `adapters/claude/skills/runtime_payload_review.md`
  - review checklist for Claude-side runtime payload usage
- `adapters/generic/client_examples/runtime_client.py`
  - minimal runtime payload consumer example

### Integration Notes
- Runtime scaffolds may inspect `context_diagnostics`, `runtime_payload`, and trust reports.
- Execution handoff still writes structured deltas through MCP.
- No runtime should bypass `MemoryTools`.

### Minimal Tests
- runtime route smoke test
- runtime bridge capability map smoke test
- runtime payload packer import and output shape test

## Phase 13 — Multi-Agent Coordination and Shared Session State

### Goal
Coordinate multiple memory clients over the same durable substrate.

### Modules
- `apps/compiler/planners/coordination_plan.py`
  - plans which packs and scopes different agents should receive
- `apps/workers/session_coordination_worker.py`
  - assembles coordination snapshots for parallel agents
- `prompts/planner/coordination_plan.md`
  - prompt template for multi-agent allocation and handoff
- `storage/docs/sessions/session_handoff.template.json`
  - structured handoff artifact between agents
- `adapters/generic/client_examples/handoff_client.py`
  - example of agent-to-agent handoff using canonical deltas

### Integration Notes
- Coordination artifacts must remain structured and delta-based.
- Link-aware retrieval should prioritize shared entities and decisions.
- Session handoff does not change the `context_pack` schema.

### Minimal Tests
- coordination planner import and smoke run
- handoff template presence test
- coordination worker smoke test

## Phase 14 — Policy, Approval Gates, and Controlled Automation

### Goal
Introduce explicit approval and policy checkpoints for higher-risk memory changes.

### Modules
- `apps/writeback/approval.py`
  - non-destructive approval-plan generation for high-impact writes
- `apps/workers/policy_audit_worker.py`
  - scans trust, hygiene, and snapshot reports for policy violations
- `prompts/validators/policy_gate.md`
  - validation template for approval-required operations
- `storage/docs/rules/policy_gate.template.md`
  - human-readable approval rule template
- `adapters/codex/policy.template.toml`
  - adapter policy configuration example

### Integration Notes
- Policy checks should consume trust and hygiene reports already exposed by MCP.
- Approval gates should annotate actions, not mutate memory directly.

### Minimal Tests
- approval planner importability
- policy audit worker smoke test
- policy template presence test

## Phase 15 — Observability and Operational Playbooks

### Goal
Complete the transition from runnable prototype to maintainable memory platform.

### Modules
- `apps/gateway/routes/operations.py`
  - route helpers for backup, recovery, and health reporting
- `apps/workers/reporting_worker.py`
  - bundles tier, trust, hygiene, and snapshot reports
- `prompts/validators/operations_review.md`
  - operational review checklist template
- `storage/exports/operations_report.template.json`
  - exported operations report structure
- `storage/archives/recovery_notes.template.md`
  - recovery notes template for drills and incidents
- `adapters/generic/client_examples/ops_client.py`
  - example operational client for exports and reports

### Integration Notes
- Observability surfaces should remain read-only unless explicitly invoking import/export actions.
- Generated reports should reuse canonical MCP methods rather than duplicating service logic.

### Minimal Tests
- reporting worker smoke test
- operations route smoke test
- export/report template presence test
