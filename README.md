# Agent Memory OS

Agent Memory OS is a shared memory kernel for Codex, Claude/Cloud, and other AI agents.

Current release: **0.10.0**

It is designed to solve a recurring problem in multi-agent systems:

- important knowledge gets fragmented across tools
- chat history becomes the de facto memory layer
- token usage grows too fast
- agents forget decisions, rules, and context between tasks
- each agent ends up with a separate, inconsistent view of reality

Agent Memory OS provides a single canonical memory layer and a context compilation system that delivers only the smallest useful context to each agent.

---

## Vision

Build a memory-first operating layer for AI agents.

Instead of treating each model or tool as an isolated intelligence with its own temporary context, Agent Memory OS treats all agents as clients of a shared memory system.

The memory system is responsible for:

- storing durable facts
- storing project rules and identity
- tracking decisions
- preserving session outcomes
- exposing memory through standard interfaces
- compiling compact task-specific context packs
- reducing token usage without losing continuity

---

## Core Goals

1. **Shared canonical memory**
   All agents read from and write to a common memory kernel.

2. **Low-token operation**
   Raw history is not passed directly to models. Context is compiled under a strict budget.

3. **Long-term continuity**
   Decisions, rules, identity, and important facts persist across sessions and across agent boundaries.

4. **Structured writeback**
   Session results are written back as deltas, not as bloated full-history summaries.

5. **Standard integration**
   Memory is exposed through an MCP interface and internal APIs.

6. **Governed truth**
   Important facts require source, status, and traceability.

---

## Non-Goals

Agent Memory OS is not intended to be:

- a raw transcript archive used directly as model context
- a replacement for version control
- a place to store secrets in general-purpose memory
- a monolithic agent runtime that forces one model provider
- an excuse to skip architecture, governance, or validation

---

## System Model

The system is organized around a few core layers:

- **Memory Kernel**  
  Canonical storage and memory APIs

- **Context Compiler**  
  Builds compact task-specific context packs

- **Writeback Engine**  
  Converts outcomes into structured deltas

- **Retrieval Engine**  
  Searches memory and ranks relevance

- **MCP Gateway**  
  Standard interface for agents and tools

- **Governance Layer**  
  Rules, source tracking, confidence, and status

---

## Memory Layers

Agent Memory OS separates memory into distinct layers:

### 1. Identity Memory
Stable project identity, guiding principles, operating assumptions, and user or organization preferences.

### 2. Procedural Memory
Workflows, checklists, playbooks, execution methods, and operational rules.

### 3. Semantic Memory
Structured knowledge about modules, systems, entities, capabilities, and concepts.

### 4. Episodic Memory
Task outcomes, session deltas, notable events, and execution traces.

### 5. Working Memory
Short-lived task-local state used during active work.

---

## First Principles

1. Shared memory is canonical.
2. Raw chat history must never be injected directly into model context.
3. Context must be compiled under a strict token budget.
4. Important facts must have source and status.
5. Session writeback must be delta-based.
6. Agents are memory clients, not memory owners.
7. Durable rules and identity are stored separately from task-local state.
8. Memory retrieval must be relevance-gated and traceable.
9. Compression is a system responsibility, not an afterthought.
10. Storage is not the same thing as usable context.

---

## Repository Status

Current status: **startup-ready / canonical Phase 6–15 scaffolds present**

This repository is being initialized with:

- core architecture documents
- merged roadmap through Phase 15
- architectural decisions
- schemas
- bootstrap contracts for memory, context, and writeback

Implementation documents, adapters, storage details, and MCP contracts are added after the architecture nucleus is stabilized.

---

## Initial Deliverables

- `docs/architecture.md`
- `docs/roadmap.md`
- `docs/visuals/*.md`
- `docs/decisions/*.md`
- base schemas
- MCP tool/resource contracts
- bootstrap storage structure
- minimal memory core scaffold

---

## Repository Structure

The repository is organized so durable memory contracts, runtime surfaces, and
future operational scaffolds remain distinct:

- `brain/`
  - canonical models, memory API, services, and adapters
- `mcp/`
  - tool, prompt, resource, and server scaffolds for agent integration
- `apps/`
  - gateway, compiler, writeback, and worker application facades
- `storage/`
  - document templates, snapshots, exports, and archive artifacts
- `prompts/`
  - reusable compiler, planner, summarizer, and validator prompt templates
- `adapters/`
  - agent-specific configuration and client examples
- `docs/`
  - architecture, roadmap, visuals, operations, security, and rollout docs
- `tests/`
  - smoke tests and integration coverage for the canonical surfaces

---

## Quickstart

### Local development

1. Copy `.env.example` to `.env`
2. Install dev dependencies:
   - `make dev-install`
3. Run focused validation:
   - `make test-fast`
4. Run smoke entrypoints:
   - `make run-gateway`
   - `make run-compiler`
   - `make run-writeback`

### Docker development

1. Copy `.env.example` to `.env`
2. Start the stack:
   - `make docker-up`
3. Inspect logs:
   - `make docker-logs`
4. Shut the stack down:
   - `make docker-down`

### Current runtime model

The repository is startup-ready for local development and smoke validation.
Many app surfaces are still transport-neutral scaffolds rather than full
long-running API servers. The canonical implementation path today is:

1. adapters call MCP tools
2. MCP delegates to the canonical Memory API
3. Memory API coordinates retrieval, compilation, writeback, trust, hygiene,
   tiering, persistence, and runtime payload helpers

---

## Intended Integrations

Agent Memory OS is intended to support:

- Codex
- Claude / Cloud Code
- local agent runtimes
- generic orchestration layers
- future custom agents and automation systems

The goal is not to optimize only for one tool, but to create a stable memory substrate all of them can use.

---

## Why This Exists

Most agent stacks fail for the same reason:

- they confuse chat history with memory
- they over-send context
- they do not preserve decisions structurally
- they cannot keep continuity between sessions
- they have no canonical truth layer

Agent Memory OS exists to fix that.

---

## Near-Term Plan

1. Freeze architecture and ADRs
2. Define schemas and contracts
3. Bootstrap memory core
4. Implement context compiler MVP
5. Add agent adapters
6. Add governance, promotion, and health checks

## Roadmap Status

The main roadmap in `docs/roadmap.md` is the canonical planning document and now
covers Phase 0 through Phase 15 in one place. Supporting visuals live in
`docs/visuals/` and summarize the architecture, compile-to-writeback workflow,
and Phase 6–15 integration path.

---

## License

TBD
