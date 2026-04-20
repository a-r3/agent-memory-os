# Token Budgeting for Agent Memory OS

## Overview

All agents in the system operate with a **token budget** to ensure:

- Efficient memory retrieval
- Controlled context size
- Prevention of exceeding model or environment limits

This document defines the **budgeting rules, enforcement, and usage patterns** for the Agent Memory OS.

---

## 1. Budget Allocation

Each task execution has a **total token budget**:

| Budget Type | Description | Default |
|------------|-------------|---------|
| Total Tokens | Maximum combined tokens for context + output | 4096 |
| Output Tokens | Reserved tokens for agent response | 512 |
| Context Tokens | Remaining tokens for context_pack | 3584 |

---

## 2. Context Compilation

- `ContextCompiler.compile_context_pack(...)` enforces token budgets.
- Context selection algorithm:
  1. Reserve output tokens first.
  2. Select memory entries, decisions, deltas, and entities.
  3. Trim candidates to fit within **remaining context tokens**.
  4. Discard archived, superseded, or out-of-scope items.

- The compiled `context_pack` always matches `schemas/context_pack.schema.json`.

---

## 3. Budget Enforcement

- All adapters (Codex, Claude) request context_pack via MCP.
- MCP delegates to `MemoryTools.context_compile(...)`.
- Token budgeting is **centralized in the compiler**, not the adapters.
- Any over-budget content is **truncated** according to priority:
  - Rules > Identity > Knowledge > Recent > Tools

---

## 4. Monitoring and Logging

- Each `context_pack` includes `limits` object:
  - `max_total_tokens`
  - `max_output_tokens`
- Adapters and MCP may log token usage for monitoring.

---

## 5. Notes

- Conservative token counting is used (built-in estimator).
- Future upgrades may include tokenizer-based accurate counts.
- Ensures **efficient, repeatable, and safe memory usage** for all agents.
