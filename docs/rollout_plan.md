# Agent Memory OS — Rollout Plan

## Overview

This document describes the **planned sequence for implementing and deploying Agent Memory OS modules**. The plan follows the architecture and roadmap to ensure a stable MVP.

---

## 1. Phase 1 — Schemas and Contracts

- `brain/models/` — MemoryEntry, Decision, SessionDelta, Entity
- `brain/services/context_compiler.py` — ContextCompiler MVP
- `mcp/tools.py` — MemoryTools skeleton
- Goal: Ensure canonical memory objects and context_pack generation

---

## 2. Phase 2 — Memory Core MVP

- Implement canonical memory read/write flows
- Include:
  - `brain/api/memory_api.py`
  - `brain/services/retrieval.py`
  - `brain/services/writeback.py`
  - MCP delegation through the Memory API
- Goal: ensure memory create/read/update/link flows work end-to-end

---

## 3. Phase 3 — Context Compiler and Retrieval Quality

- Implement:
  - `brain/services/context_compiler.py`
  - `brain/services/retrieval.py`
  - `brain/services/context_pack_validation.py`
- Include:
  - status- and scope-aware filtering
  - deterministic ranking
  - token-budget enforcement
  - schema-shaped `context_pack` output

---

## 4. Phase 4 — MCP Integration

- MCP orchestrates:
  - Memory API
  - Retrieval backend
  - ContextCompiler
- `MemoryTools.context_compile(...)` is the central entrypoint
- Ensure schema compliance and token budgeting enforcement

---

## 5. Phase 5 — Agent Adapters

- Implement thin adapters for Codex, Claude, and generic runtimes
- Methods:
  - `execute_task(task: str, agent_id: str)`
  - request `context_pack` via MCP
  - stub execution
  - structured delta writeback
- Adapters must remain **thin**: memory clients only

---

## 6. Phase 6 — Retrieval Intelligence and Links

- Implement:
  - relationship traversal
  - link-aware ranking
  - relationship-aware prioritization for context compilation
- Keep retrieval centralized in `brain/services/retrieval.py`

---

## 7. Phase 7 — Memory Hygiene

- Implement:
  - promotion and dedupe suggestions
  - link validation
  - memory health reporting
- Keep all reads through the canonical Memory API

---

## 8. Testing and Validation

- Python compile checks (`py_compile`)
- Integration tests for:
  - `MemoryTools.context_compile(...)`
  - adapters through MCP
  - Memory API linking and writeback
  - Phase 6 traversal and link-aware retrieval
  - Phase 7 hygiene reporting
- Ensure context_pack is schema-shaped
- Validate token budgets, status/scope filtering, deterministic ranking, and link consistency

---

## 7. Notes

- Follow the roadmap in `docs/Roadmap.md` and decisions in ADR1–ADR6
- Maintain module paths and naming conventions
- Future phases:
  - Persistent storage
  - Real Codex/Claude runtime
  - Advanced retrieval ranking
