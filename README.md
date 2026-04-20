# Agent Memory OS

Version: **0.10.0**  
Status: **startup-ready**  
Release state: **Phase 15 complete**

Agent Memory OS is a shared memory kernel and context operating layer for AI
agents such as Codex, Claude/Cloud, and future generic runtimes. Its purpose is
to make memory canonical, keep prompt-time context compact, and let multiple
agents operate over the same durable substrate without relying on raw chat
history.

The repository is organized around one architectural rule: durable memory,
prompt-time context, runtime handoff, and writeback are separate responsibilities.
Memory is the source of truth. `context_pack` is a compiled projection. Adapters
are thin clients. MCP is the stable integration surface.

---

## Overview

Multi-agent systems usually fail in the same ways:

- important decisions are scattered across tools and sessions
- raw conversation history becomes the default memory layer
- prompt size grows faster than useful context
- different agents get different versions of the same project truth
- writeback is ad hoc, unstructured, or impossible to audit

Agent Memory OS addresses those problems by centralizing:

- structured memory storage
- context compilation under token budget
- link-aware retrieval
- trust-aware write validation
- delta-based writeback
- runtime payload preparation
- hygiene, tiering, persistence, and operational reporting

The result is a memory-first system where agents are replaceable clients of a
shared canonical layer rather than isolated runtimes with fragile local context.

---

## Canonical Architecture

The repository follows a layered model:

1. **Memory is canonical**
   Durable facts, rules, decisions, entities, and session deltas live behind the
   canonical `MemoryAPI`.

2. **Context is compiled**
   Agents do not receive raw history. They receive a compact, schema-shaped
   `context_pack` compiled from relevant memory under a token budget.

3. **Adapters stay thin**
   Codex, Claude, and generic adapters ask MCP for context, perform work, and
   write structured deltas back through the canonical path.

4. **MCP is the universal surface**
   Tools, prompts, and resources are exposed through `mcp/` so transports and
   agent clients integrate through one stable contract.

5. **Writeback is governed**
   Memory writes pass through trust checks, source/status expectations, and later
   policy or approval gates.

6. **Operations remain traceable**
   Hygiene, tiering, snapshots, exports, runtime payloads, and reports all stay
   connected to the same core system instead of becoming side systems.

### Core runtime flow

1. An adapter or app requests context through MCP.
2. MCP delegates to `MemoryAPI`.
3. `MemoryAPI` coordinates retrieval, ranking, linking, budgeting, validation,
   summarization, and trust checks.
4. A schema-compliant `context_pack` is returned.
5. Optional runtime payloads are built for provider-facing execution handoff.
6. Task outcomes are written back as structured session deltas, decisions, or
   memory entries.
7. Hygiene, tiering, persistence, coordination, policy, and reporting layers
   consume the same canonical surfaces.

---

## Visuals

The repository now includes generated SVG diagrams in `docs/visuals/` so the
README can embed architecture and workflow visuals directly. The original
markdown diagram sources remain available alongside the SVG assets for review
and maintenance.

### 1. Architecture Overview

This illustration maps the actual canonical structure of the repository:
adapters and provider templates flow into MCP, MCP delegates to `MemoryAPI`,
and `MemoryAPI` coordinates core services, app facades, schemas, prompts,
tests, and storage artifacts.

![Architecture Overview](docs/visuals/architecture_overview.svg)

*Caption: `architecture_overview.svg` shows how `brain/adapters/`, `mcp/`,
`brain/api/memory_api.py`, `brain/services/`, `apps/`, `schemas/`, `storage/`,
`prompts/`, and `tests/` fit together through the canonical architecture. The
source markdown version is [docs/visuals/architecture_overview.md](/home/oem/Documents/01_Projects/agent-memory-os/docs/visuals/architecture_overview.md).*

### 2. Compile-to-Writeback Workflow

This workflow illustration follows the repository’s real execution path:
adapter or app request, MCP tool entry, `MemoryAPI` orchestration, retrieval and
validation, trust checks, `context_pack` creation, runtime payload shaping,
execution handoff, structured writeback, and downstream hygiene, persistence,
and reporting.

![Compile to Writeback Workflow](docs/visuals/workflow_compile_execute_writeback.svg)

*Caption: `workflow_compile_execute_writeback.svg` visualizes the canonical path
from `MemoryTools.context_compile(...)` through `brain/services/context_compiler.py`,
`brain/services/trust.py`, runtime payload packers, structured delta writeback,
and Phase 11–15 persistence and operations workflows. The source markdown
version is [docs/visuals/workflow_compile_execute_writeback.md](/home/oem/Documents/01_Projects/agent-memory-os/docs/visuals/workflow_compile_execute_writeback.md).*

### 3. Phase 6–15 Integration Map

This illustration presents the sequential Phase 6–15 buildout using the real
module and template paths in the repository. It emphasizes that later phases
extend the same canonical memory substrate instead of introducing separate side
systems.

![Phase 6 to 15 Integration](docs/visuals/phase6_15_integration.svg)

*Caption: `phase6_15_integration.svg` shows the progression from retrieval
intelligence and hygiene through trust, budgeting, persistence, runtime
handoff, multi-agent coordination, policy gates, and operational playbooks. The
source markdown version is [docs/visuals/phase6_15_integration.md](/home/oem/Documents/01_Projects/agent-memory-os/docs/visuals/phase6_15_integration.md).*

## Phase 6–15 Roadmap Summary

The full roadmap lives in [docs/roadmap.md](/home/oem/Documents/01_Projects/agent-memory-os/docs/roadmap.md). The summary below focuses on the implemented Phase 6–15 repository surfaces.

### Phase 6 — Retrieval Intelligence and Links

Goal: improve retrieval precision beyond plain text search.

High-level functionality:

- relationship-aware retrieval
- typed links between memory objects
- deterministic ranking and traversal support
- stale and superseded filtering

Canonical modules and paths:

- `brain/services/retrieval.py`
- `brain/services/linking.py`
- `brain/services/relationship_traversal.py`
- `brain/services/ranking.py`
- `brain/api/memory_api.py`

### Phase 7 — Promotion, Dedupe, and Memory Hygiene

Goal: prevent long-term memory decay and reduce duplication.

High-level functionality:

- promotion suggestions from repeated structured delta evidence
- duplicate candidate detection
- link validation and health reporting
- hygiene-aware reporting through the canonical API and MCP

Canonical modules and paths:

- `brain/services/memory_hygiene.py`
- `apps/writeback/promotion.py`
- `apps/writeback/dedupe.py`
- `apps/writeback/merge.py`
- `apps/writeback/main.py`

### Phase 8 — Governance and Trust Hardening

Goal: ensure important memory is traceable and unsafe content is screened.

High-level functionality:

- trust-aware write validation
- corpus trust reporting
- secret and PII detection
- governance signals attached to writeback and audit flows

Canonical modules and paths:

- `brain/services/trust.py`
- `brain/api/memory_api.py`
- `mcp/tools.py`
- `docs/security.md`

### Phase 9 — Cost and Performance Optimization

Goal: keep context useful while reducing token waste and improving reuse.

High-level functionality:

- token-budget planning and diagnostics
- pack compression
- cache-friendly prompt ordering
- hot/warm/cold tier reporting

Canonical modules and paths:

- `brain/services/budgeting.py`
- `brain/services/summarization.py`
- `brain/services/tiering.py`
- `apps/compiler/compressors/token_compressor.py`
- `apps/compiler/compressors/cache_friendly_compressor.py`
- `docs/token_budgeting.md`

### Phase 10 — Operational Readiness

Goal: make the repository runnable, testable, and operable as a startup-ready scaffold.

High-level functionality:

- operational docs and rollout guidance
- health reporting
- canonical smoke entrypoints
- deployment-oriented make targets

Canonical modules and paths:

- `apps/gateway/main.py`
- `apps/gateway/routes/health.py`
- `docs/operations.md`
- `docs/rollout_plan.md`
- `Makefile`
- `docker-compose.yml`

### Phase 11 — Persistent Storage and Replay

Goal: extend the in-memory core into durable snapshot/export/recovery flows.

High-level functionality:

- snapshot export and import scaffolds
- storage route helpers
- archive planning based on hygiene signals
- recovery worker and replay support

Canonical modules and paths:

- `apps/gateway/routes/storage.py`
- `apps/compiler/planners/cache_refresh_planner.py`
- `apps/writeback/archive.py`
- `apps/workers/recovery_worker.py`
- `storage/snapshots/snapshot_manifest.template.json`
- `storage/exports/export_manifest.template.json`
- `storage/archives/archive_manifest.template.json`
- `prompts/planner/cache_refresh_plan.md`
- `prompts/validators/snapshot_integrity.md`

### Phase 12 — Runtime Connectors and Execution Handoff

Goal: bridge compiled context into provider-facing runtime payloads without moving core logic into adapters.

High-level functionality:

- runtime payload packing
- runtime route helpers
- runtime MCP capability bridge
- provider-facing runtime guidance templates

Canonical modules and paths:

- `apps/gateway/routes/runtime.py`
- `apps/gateway/mcp/runtime_bridge.py`
- `apps/compiler/packers/runtime_payload_packer.py`
- `prompts/compiler/runtime_payload.md`
- `adapters/codex/runtime.template.md`
- `adapters/claude/skills/runtime_payload_review.md`
- `adapters/generic/client_examples/runtime_client.py`

### Phase 13 — Multi-Agent Coordination and Shared Session State

Goal: coordinate multiple memory clients across a shared durable substrate.

High-level functionality:

- coordination planning
- handoff artifacts
- coordination worker scaffolds
- structured session handoff for parallel agents

Canonical modules and paths:

- `apps/compiler/planners/coordination_plan.py`
- `apps/workers/session_coordination_worker.py`
- `prompts/planner/coordination_plan.md`
- `storage/docs/sessions/session_handoff.template.json`
- `adapters/generic/client_examples/handoff_client.py`

### Phase 14 — Policy, Approval Gates, and Controlled Automation

Goal: introduce explicit approval and policy checkpoints for higher-risk memory changes.

High-level functionality:

- approval planning for sensitive writes
- policy audit worker
- policy gate templates and validation prompts
- adapter-side policy examples

Canonical modules and paths:

- `apps/writeback/approval.py`
- `apps/workers/policy_audit_worker.py`
- `prompts/validators/policy_gate.md`
- `storage/docs/rules/policy_gate.template.md`
- `adapters/codex/policy.template.toml`

### Phase 15 — Observability and Operational Playbooks

Goal: complete the transition from runnable scaffold to maintainable operational platform.

High-level functionality:

- operational reporting
- route helpers for operations and reporting
- exported operations report structure
- recovery notes and operational client examples

Canonical modules and paths:

- `apps/gateway/routes/operations.py`
- `apps/workers/reporting_worker.py`
- `prompts/validators/operations_review.md`
- `storage/exports/operations_report.template.json`
- `storage/archives/recovery_notes.template.md`
- `adapters/generic/client_examples/ops_client.py`

---

## Usage

### Prerequisites

- Python `3.11+`
- `pip`
- optional: Docker and Docker Compose

### Install

```bash
make dev-install
```

Alternative:

```bash
python3 -m pip install -e ".[dev]"
```

### Run the canonical smoke entrypoints

Gateway facade:

```bash
make run-gateway
```

Compiler facade:

```bash
make run-compiler
```

Writeback facade:

```bash
make run-writeback
```

Workers:

```bash
make run-worker-ingest
make run-worker-compaction
make run-worker-graph
make run-worker-recovery
make run-worker-reporting
```

### Run MCP surfaces locally

Inspect the MCP server description:

```bash
python3 - <<'PY'
from mcp.server import MCPServer
import json
print(json.dumps(MCPServer().describe(), indent=2))
PY
```

Compile a context pack through MCP:

```bash
python3 - <<'PY'
from mcp.tools import MemoryTools
import json
tools = MemoryTools()
pack = tools.context_compile(agent="codex", task="summarize the repository state", budget_tokens=900)
print(json.dumps(pack, indent=2))
PY
```

Preview a runtime payload:

```bash
python3 - <<'PY'
from mcp.tools import MemoryTools
import json
tools = MemoryTools()
pack = tools.context_compile(agent="codex", task="prepare runtime payload", budget_tokens=900)
payload = tools.runtime_payload_preview(agent="codex", task="prepare runtime payload", context_pack=pack)
print(json.dumps(payload, indent=2))
PY
```

### Use adapters directly

Codex adapter:

```bash
python3 - <<'PY'
from brain.adapters.codex_adapter import CodexAdapter
adapter = CodexAdapter()
result = adapter.execute_task(task="review repository memory architecture", agent_id="codex")
print(type(result).__name__)
PY
```

Claude adapter:

```bash
python3 - <<'PY'
from brain.adapters.claude_adapter import ClaudeAdapter
adapter = ClaudeAdapter()
result = adapter.execute_task(task="summarize operational readiness", agent_id="claude")
print(type(result).__name__)
PY
```

### Tests and validation

Full suite:

```bash
make test
```

Focused integration subset:

```bash
make test-fast
```

Compile check:

```bash
make pycompile
```

Lint and format:

```bash
make lint
make format
```

Type checking:

```bash
make typecheck
```

Build:

```bash
make build
```

### Docker

Start:

```bash
make docker-up
```

Logs:

```bash
make docker-logs
```

Stop:

```bash
make docker-down
```

---

## Integration Notes

### `context_pack` compilation

`context_pack` compilation is canonicalized through:

- `MemoryTools.context_compile(...)`
- `MemoryAPI.compile_context(...)`
- `brain/services/context_compiler.py`
- `brain/services/context_pack_validation.py`
- `schemas/context_pack.schema.json`

The compiler is responsible for:

- selecting relevant memory
- applying scope filters
- respecting inactive status filters such as archived or superseded records
- enforcing token budgets
- returning schema-shaped output

### Trust checks

Write validation flows through:

- `MemoryAPI.write_memory_entry(...)`
- `MemoryAPI.register_decision(...)`
- `MemoryAPI.write_session_delta(...)`
- `brain/services/trust.py`

Trust behavior includes:

- secret-pattern blocking
- PII detection warnings
- source reference warnings
- trust scoring and corpus-level reporting

### Token-budgeting

Budgeting flows through:

- `brain/services/budgeting.py`
- `MemoryAPI.analyze_context_pack(...)`
- `MemoryTools.context_budget_report(...)`
- `docs/token_budgeting.md`

The current repository keeps budget diagnostics separate from the canonical
pack shape so schema compliance remains stable.

### Link-aware retrieval

Link-aware retrieval depends on:

- `brain/services/retrieval.py`
- `brain/services/linking.py`
- `brain/services/relationship_traversal.py`
- `brain/services/ranking.py`

It improves retrieval precision by prioritizing connected entities, decisions,
and memory records rather than treating the corpus as flat text.

### Runtime payloads

Runtime payload construction depends on:

- `MemoryAPI.build_runtime_payload(...)`
- `MemoryTools.runtime_payload_preview(...)`
- `apps/compiler/packers/runtime_payload_packer.py`
- `apps/gateway/routes/runtime.py`
- `apps/gateway/mcp/runtime_bridge.py`

This keeps provider-facing payload shaping in the system core rather than
inside adapter logic.

### Memory hygiene

Hygiene and long-term corpus management depend on:

- `brain/services/memory_hygiene.py`
- `apps/writeback/promotion.py`
- `apps/writeback/dedupe.py`
- `apps/writeback/archive.py`
- `apps/workers/reporting_worker.py`

This is how the system avoids long-term memory drift, duplicate accumulation,
and blind operational growth.

---

## Contribution Notes

For new contributors:

1. Treat `brain/api/memory_api.py` as the canonical orchestration surface.
2. Do not bypass MCP or `MemoryAPI` when adding new entrypoints.
3. Keep adapters thin. Put memory logic in services, not agent wrappers.
4. Preserve canonical paths for Phase 6–15 modules and templates.
5. Keep `context_pack` schema-compliant. If behavior changes, update the schema,
   compiler, validator, and tests together.
6. Add tests for new retrieval, trust, budgeting, runtime, or persistence behavior.
7. Prefer minimal diffs and transport-neutral facades over framework-heavy changes.
8. Respect repository docs in `docs/`, especially architecture, roadmap,
   operations, token budgeting, security, and ADRs.

Recommended first reads:

- [docs/architecture.md](/home/oem/Documents/01_Projects/agent-memory-os/docs/architecture.md)
- [docs/roadmap.md](/home/oem/Documents/01_Projects/agent-memory-os/docs/roadmap.md)
- [docs/operations.md](/home/oem/Documents/01_Projects/agent-memory-os/docs/operations.md)
- [docs/token_budgeting.md](/home/oem/Documents/01_Projects/agent-memory-os/docs/token_budgeting.md)
- [docs/security.md](/home/oem/Documents/01_Projects/agent-memory-os/docs/security.md)
- [docs/rollout_plan.md](/home/oem/Documents/01_Projects/agent-memory-os/docs/rollout_plan.md)
- [docs/decisions/README.md](/home/oem/Documents/01_Projects/agent-memory-os/docs/decisions/README.md)

---

## References

Architecture and planning:

- [docs/architecture.md](/home/oem/Documents/01_Projects/agent-memory-os/docs/architecture.md)
- [docs/roadmap.md](/home/oem/Documents/01_Projects/agent-memory-os/docs/roadmap.md)
- [docs/rollout_plan.md](/home/oem/Documents/01_Projects/agent-memory-os/docs/rollout_plan.md)

Operations and governance:

- [docs/operations.md](/home/oem/Documents/01_Projects/agent-memory-os/docs/operations.md)
- [docs/token_budgeting.md](/home/oem/Documents/01_Projects/agent-memory-os/docs/token_budgeting.md)
- [docs/security.md](/home/oem/Documents/01_Projects/agent-memory-os/docs/security.md)

Schemas:

- [schemas/context_pack.schema.json](/home/oem/Documents/01_Projects/agent-memory-os/schemas/context_pack.schema.json)
- [schemas/event.schema.json](/home/oem/Documents/01_Projects/agent-memory-os/schemas/event.schema.json)
- [schemas/session_delta.schema.json](/home/oem/Documents/01_Projects/agent-memory-os/schemas/session_delta.schema.json)
- [schemas/entity.schema.json](/home/oem/Documents/01_Projects/agent-memory-os/schemas/entity.schema.json)

Visual workflows:

- [docs/visuals/architecture_overview.svg](/home/oem/Documents/01_Projects/agent-memory-os/docs/visuals/architecture_overview.svg)
- [docs/visuals/workflow_compile_execute_writeback.svg](/home/oem/Documents/01_Projects/agent-memory-os/docs/visuals/workflow_compile_execute_writeback.svg)
- [docs/visuals/phase6_15_integration.svg](/home/oem/Documents/01_Projects/agent-memory-os/docs/visuals/phase6_15_integration.svg)
- [docs/visuals/architecture_overview.md](/home/oem/Documents/01_Projects/agent-memory-os/docs/visuals/architecture_overview.md)
- [docs/visuals/workflow_compile_execute_writeback.md](/home/oem/Documents/01_Projects/agent-memory-os/docs/visuals/workflow_compile_execute_writeback.md)
- [docs/visuals/phase6_15_integration.md](/home/oem/Documents/01_Projects/agent-memory-os/docs/visuals/phase6_15_integration.md)

---

## License

Proprietary. See repository policy and maintainer guidance before redistribution.
