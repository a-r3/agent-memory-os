# Agent Memory OS Roadmap

## Purpose

This roadmap defines the staged development path for Agent Memory OS.

The roadmap is intentionally architecture-first. The goal is not to rush into implementation before the system's memory model, governance model, and integration model are stable.

---

## Guiding Strategy

Development follows these priorities:

1. freeze architectural intent
2. define durable contracts
3. implement the smallest useful memory core
4. enable compact context compilation
5. connect real agents
6. harden governance and trust
7. optimize for scale and token efficiency

---

## Phase 0 — Architecture Nucleus

### Goal
Establish the canonical conceptual foundation of the system.

### Outcomes
- README finalized for bootstrap
- architecture document created
- roadmap document created
- ADR set created
- initial terminology frozen
- repository structure agreed

### Deliverables
- `README.md`
- `docs/architecture.md`
- `docs/roadmap.md`
- `docs/decisions/*.md`

### Exit Criteria
- core terminology is stable
- high-level architecture is approved
- major design principles are documented
- bootstrap repository structure is accepted

---

## Phase 1 — Schemas and Contracts

### Goal
Define the structural contracts of memory.

### Outcomes
- canonical object types defined
- schema set created
- naming conventions frozen
- object lifecycle model documented
- context pack structure defined

### Deliverables
- `schemas/context_pack.schema.json`
- `schemas/event.schema.json`
- `schemas/session_delta.schema.json`
- `schemas/entity.schema.json`
- `brain/models/*.py`

### Exit Criteria
- schemas validate cleanly
- memory objects are unambiguous
- writeback and retrieval contracts are clear
- context compiler has a stable target structure

---

## Phase 2 — Memory Core MVP

### Goal
Implement the first working canonical memory layer.

### Outcomes
- memory create/read/update path works
- decision registration works
- session delta storage works
- basic search works
- storage layout works

### Deliverables
- memory API scaffold
- initial storage structure
- CRUD logic for core objects
- basic indexing strategy

### Exit Criteria
- memory entries can be stored and retrieved
- decisions can be registered separately
- session deltas can be written and read
- object status and source fields are enforced

---

## Phase 3 — Context Compiler MVP

### Goal
Make memory usable under strict token budgets.

### Outcomes
- task intent to memory scope pipeline exists
- relevant memory can be selected and filtered
- context pack generation works
- budget limits are enforced
- compact context becomes the default runtime path

### Deliverables
- context compiler contract
- relevance ranking rules
- compression tiers
- pack assembly logic
- budget manager
- `brain/services/context_compiler.py`
- `brain/services/retrieval.py`

### Exit Criteria
- raw history is not needed for normal operation
- compact context packs can be generated
- context packs remain within configured limits
- the compiler can separate rules, identity, and recent context

---

## Phase 4 — MCP Interface and Tool Surface

### Goal
Expose the system through a clean integration layer.

### Outcomes
- MCP server scaffold exists
- resources are defined
- tools are defined
- prompts are defined
- external agents can access memory capabilities through one interface

### Deliverables
- MCP server
- resource catalog
- tool catalog
- reusable prompt catalog
- `mcp/tools.py`
- `mcp/resources.py`

### Exit Criteria
- memory read/write flows are reachable through MCP
- context compilation is reachable through MCP
- core tool and resource names are stable
- external integration path is ready

---

## Phase 5 — Agent Adapters

### Goal
Enable real multi-agent usage.

### Outcomes
- Codex adapter exists
- Claude adapter exists
- generic adapter contract exists
- writeback happens after task completion
- memory continuity works across agent boundaries

### Deliverables
- adapter skeletons
- adapter-specific instructions/contracts
- writeback integration hooks
- `brain/adapters/codex_adapter.py`
- `brain/adapters/claude_adapter.py`

### Exit Criteria
- at least two agent environments can use shared memory
- session deltas appear from real agent runs
- decision registration can happen from agent workflows
- agents behave as memory clients instead of isolated runtimes

---

## Phase 6 — Retrieval Intelligence and Links

### Goal
Improve relevance and structure.

### Outcomes
- entity linking exists
- graph relationships begin to form
- stale filtering exists
- superseded decisions are handled cleanly
- retrieval quality improves

### Deliverables
- entity model
- link model
- relationship storage
- ranking improvements
- stale/superseded handling

### Exit Criteria
- memory retrieval is more precise than plain text search
- linked decisions and components can be traversed
- obsolete items are less likely to pollute active context
- system relationships become visible

---

## Phase 7 — Promotion, Dedupe, and Memory Hygiene

### Goal
Prevent long-term memory decay.

### Outcomes
- working memory promotion exists
- duplicate memory can be merged
- archive tiers exist
- memory health checks begin

### Deliverables
- promotion rules
- dedupe rules
- archive flow
- memory health report

### Exit Criteria
- repeated facts are reduced
- long-term memory is cleaner
- working memory can graduate into durable memory intentionally
- hygiene checks can detect drift and redundancy

---

## Phase 8 — Governance and Trust Hardening

### Goal
Make the system robust against noisy or unsafe memory.

### Outcomes
- trust-aware writeback exists
- secret detection rules exist
- source enforcement improves
- unverified memory is clearly separated
- health and traceability improve

### Deliverables
- trust scoring rules
- source validation rules
- secret and sensitive-data safeguards
- audit/report surfaces

### Exit Criteria
- important memory is traceable
- unverified content is not confused with approved truth
- governance signals influence retrieval and promotion
- memory poisoning risks are reduced

---

## Phase 9 — Cost and Performance Optimization

### Goal
Reduce token waste and operational overhead.

### Outcomes
- hot/warm/cold memory tiers exist
- caching strategy improves
- prompt ordering becomes more cache-friendly
- retrieval latency improves
- compiler efficiency improves

### Deliverables
- tiered memory strategy
- token analytics
- context compression improvements
- optimization reports

### Exit Criteria
- average context cost falls
- repeated tasks reuse stable context more efficiently
- retrieval and packing become faster
- system remains compact as memory grows

---

## Phase 10 — Operational Readiness

### Goal
Prepare the system for broader real-world use.

### Outcomes
- operational docs exist
- failure handling is defined
- health checks exist
- backup/export paths exist
- rollout patterns are documented

### Deliverables
- operations guide
- recovery guide
- export/backup contracts
- deployment notes

### Exit Criteria
- system can be run and maintained consistently
- failure modes are documented
- recovery paths exist
- operational maturity is acceptable

---

## Roadmap Discipline

The roadmap should follow these rules:

1. do not skip architecture and contracts
2. do not overbuild before the compiler exists
3. do not connect agents before memory rules are stable
4. do not optimize before baseline flows work
5. do not expand governance until core writeback exists

---

## Immediate Next Focus

The current focus is:

- freeze architecture
- freeze ADRs
- prepare schemas
- bootstrap repository structure

This is the correct order because everything else depends on it.

---

## Summary

Agent Memory OS should not be built as a pile of tools.

It should be built in stages:

- first as a coherent architecture
- then as a governed memory system
- then as a compact context system
- then as a shared runtime substrate for agents

That sequence is the roadmap.
