# Agent Memory OS Architecture

## 1. Purpose

Agent Memory OS is a shared memory kernel and context operating layer for AI agents.

Its purpose is to let multiple agents operate over the same durable memory without depending on raw chat history and without repeatedly paying large token costs for the same context.

The system is designed around a central principle:

> persistent memory must be separated from prompt-time context, and prompt-time context must be compiled under budget.

---

## 2. Problem Statement

Multi-agent systems often suffer from the following failure modes:

- memory fragmentation across tools and sessions
- uncontrolled prompt growth
- repeated re-explanation of stable facts
- lack of durable decision records
- no source attribution for important facts
- inconsistent behavior between different agents
- weak continuity across sessions

These problems are not primarily model problems. They are memory architecture problems.

Agent Memory OS addresses them by making memory a first-class system component.

---

## 3. Architectural Thesis

The system is memory-centric, not agent-centric.

That means:

- agents are replaceable clients
- memory is the canonical layer
- retrieval and context compilation are centralized responsibilities
- durable knowledge is stored structurally
- prompt-time context is a projection, not the source of truth

This design intentionally separates:

1. **what the system knows**
2. **what the system stores**
3. **what the agent receives for one task**

Those three things must not be treated as identical.

---

## 4. High-Level Architecture

```text
[User / Repo / Files / Tasks]
            |
            v
   [Brain Gateway / MCP Server]
            |
     +------+------+--------------------+
     |             |                    |
     v             v                    v
 [Memory API] [Context Compiler] [Writeback Engine]
     |             |                    |
     |             |                    |
     v             v                    v
 [Rules Store] [Retrieval Engine] [Event / Delta Log]
     |             |                    |
     v             v                    v
 [Doc Store] [Vector Layer] [Graph / Link Layer]
```

---

## 5. Core Components

### 5.1 Brain Gateway / MCP Server

This is the main integration surface for agents.

Responsibilities:

- expose memory resources
- expose tools
- expose reusable prompts
- normalize access across agents
- provide a stable external interface

This layer allows Codex, Claude, and other systems to interact with the same memory kernel.

### 5.2 Memory API

The Memory API is the canonical interface to stored memory.

Responsibilities:

- create entries
- update entries
- retrieve entries
- link entries
- register decisions
- read session deltas
- manage status and traceability

This API is the authoritative path into durable memory.

### 5.3 Context Compiler

The Context Compiler is the most important runtime component.

Responsibilities:

- interpret task intent
- determine relevant memory scopes
- retrieve candidate items
- rank and filter them
- compress and package them
- enforce token budgets
- produce agent-specific context packs

The compiler transforms durable storage into minimal useful context.

Without this layer, storage growth turns into context bloat.

### 5.4 Retrieval Engine

The Retrieval Engine finds relevant memory for a task.

Responsibilities:

- semantic search
- entity-aware lookup
- decision lookup
- recent session lookup
- relevance ranking
- stale or superseded filtering

The Retrieval Engine should support layered retrieval:

- coarse retrieval
- reranking
- compression
- final selection

### 5.5 Writeback Engine

The Writeback Engine converts execution outcomes into durable memory changes.

Responsibilities:

- produce session deltas
- register decisions
- create or update facts
- classify uncertainty
- mark entries as verified or unverified
- avoid duplication where possible

The writeback model is deliberately delta-based to control storage and token growth.

### 5.6 Rules Store

The Rules Store contains stable operational guidance.

Examples:

- project principles
- architecture rules
- workflow constraints
- output formatting requirements
- compliance rules
- security constraints

Rules are stored separately from episodic task history because they are stable and frequently reused.

### 5.7 Event / Delta Log

This is the append-only history of what happened.

Examples:

- agent actions
- session outcomes
- context compilation requests
- major execution events
- errors
- writeback operations

This log is primarily for traceability and episodic continuity, not for raw prompt injection.

### 5.8 Storage Layers

#### Document Store

Stores markdown, JSON, YAML, and other structured artifacts.

Used for:

- architecture documents
- ADRs
- identity memory
- rules
- session summaries
- memory cards

#### Vector Layer

Supports semantic retrieval of relevant memory entries.

Used for:

- fuzzy recall
- concept similarity
- prior examples
- natural language search

#### Graph / Link Layer

Supports typed relationships between entities.

Used for:

- impacts
- dependencies
- ownership
- module relationships
- decision-to-component links

The graph layer is important because memory is not only a bag of facts; it is also a network of relationships.

## 6. Memory Model

Agent Memory OS defines five memory layers.

### 6.1 Identity Memory

Contains durable identity and stable preferences.

Examples:

- project purpose
- mission and philosophy
- non-negotiable rules
- preferred output styles
- architectural posture
- user-level durable preferences

Identity memory changes rarely and is often reusable across many tasks.

### 6.2 Procedural Memory

Contains operational methods and workflows.

Examples:

- how phase gates work
- how closeout is written
- how reviews are performed
- how tasks are escalated
- how outputs must be structured

Procedural memory tells the system how to behave.

### 6.3 Semantic Memory

Contains durable knowledge about the system and domain.

Examples:

modules
components
capabilities
entities
terms
architecture concepts

Semantic memory is often retrieved through vector search and entity linking.

6.4 Episodic Memory

Contains structured records of what happened.

Examples:

session outcomes
task deltas
execution results
notable incidents
previous solutions

Episodic memory is not intended to replace stable knowledge, but to preserve continuity and traceability.

6.5 Working Memory

Contains short-lived task-local context.

Examples:

current branch focus
active subproblem
immediate constraints
open questions in the current task

Working memory should not automatically become durable memory. Promotion must be explicit or rule-based.

7. Context Architecture
7.1 Why Raw History Is Rejected

Raw history is a poor memory layer because it is:

expensive
noisy
hard to validate
hard to query
unstable in relevance
vulnerable to prompt drift

Therefore, the system does not use raw history as canonical context.

7.2 Context Pack Model

Agents receive a compiled context pack, not the whole memory base.

A context pack is expected to include:

rules pack
identity pack
knowledge pack
recent pack
tool hints
token limits

This structure allows the system to deliver the smallest useful context instead of the largest available context.

7.3 Budgeted Compilation

Every context pack is compiled under a budget.

The compiler must decide:

what is essential
what can be compressed
what can be omitted
what should stay as retrievable memory rather than prompt content

The context compiler is therefore both a retrieval system and a budget enforcement system.

8. Canonical Objects

The architecture assumes a few key durable object types.

Memory Entry

A structured memory unit containing a fact, rule, note, identity item, or procedure.

Decision

A durable architectural or workflow decision stored separately from ordinary memory notes.

Event

A structured execution event.

Session Delta

A compact record of what changed in a session.

Entity

A typed representation of a system concept, module, capability, or object.

Context Pack

A compiled task-specific bundle built for one agent invocation.

9. Agent Integration Model
9.1 Agent Adapters

Each agent is integrated through an adapter layer.

Adapters are responsible for:

requesting compiled context
translating context into agent-appropriate format
invoking tools or resources
writing back task outcomes

Adapters should remain thin. They do not own business logic or durable memory logic.

9.2 Codex Adapter

The Codex adapter is responsible for:

invoking the context compiler
converting memory outputs into Codex-friendly instruction/input format
collecting execution outcomes
writing back deltas and decisions
9.3 Claude / Cloud Adapter

The Claude adapter is responsible for:

exposing MCP tools and resources
leveraging project instructions and local skills
requesting compiled context as needed
writing back structured deltas after work
9.4 Generic Adapter

A generic adapter supports:

future agent runtimes
orchestration systems
local automation pipelines
custom integrations

The memory model must outlive any one vendor or agent.

10. Governance and Trust

The system must distinguish between:

draft
unverified
verified
approved
superseded
archived

Important facts should not be treated as equivalent to verified truth unless they have source and status.

The architecture assumes:

source references
confidence signals
status fields
traceability
decision lineage
supersession handling

This prevents the memory system from becoming a self-reinforcing store of unvalidated claims.

11. Security Posture

General memory must not be used as a secret store.

The architecture must support:

secret detection
PII marking
write restrictions
trust-aware retrieval
auditable writes
memory repair or rollback where needed

Security-sensitive material should live outside general-purpose memory or behind explicit controls.

12. Operational Principles
Durable memory is canonical.
Prompt-time context is compiled.
Full history is not canonical context.
Session writeback is delta-first.
Facts require source and status.
Decisions are first-class objects.
Stable rules are separated from episodic outcomes.
Retrieval must filter stale and superseded items.
Compression is mandatory.
Agents remain replaceable.
13. MVP Boundary

The initial MVP focuses on:

documenting the architecture
defining schemas
bootstrapping a memory core
adding a context compiler contract
defining MCP tools and resources
preparing thin adapters for Codex and Claude

The MVP does not yet require:

advanced graph reasoning
full multi-tenant security
complex orchestration
autonomous self-modification
heavyweight distributed infrastructure

Those are later-phase concerns.

14. Expected Evolution

The system is expected to evolve in this order:

architecture and governance nucleus
schema and storage contracts
memory core
context compiler MVP
agent adapters
graph/link layer
promotion and dedupe
health reports and trust checks
optimization and cost control

This keeps the system grounded and prevents premature complexity.

15. Summary

Agent Memory OS is not simply a storage system.

It is a governed memory substrate and context operating layer for AI agents.

Its purpose is not to keep everything in the prompt.
Its purpose is to preserve continuity, minimize token waste, and ensure that multiple agents can operate over the same durable truth layer.

That is the architectural center of gravity of the system.
