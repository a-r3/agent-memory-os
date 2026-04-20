# Security Guidelines for Agent Memory OS

## Overview

This document defines security rules and best practices for **Agent Memory OS** to ensure safe and controlled operation of agents, memory storage, and MCP integration.  

It covers **data protection, access control, agent responsibilities, and system integrity**.

---

## 1. Access Control

- **Agents** can only read/write memory through the **MCP API**.
- Direct access to `brain/` objects or storage is forbidden.
- Access is **role-based**:
  - Codex, Claude: read/write context_pack
  - Retrieval backend: read memory entries
  - Adapters: execute tasks using MCP, no direct memory mutation

---

## 2. Data Protection

- No **raw user input** or chat history may be stored in canonical memory.
- Sensitive data (PII, secrets, tokens) must never appear in context_pack.
- All session deltas must be **structured**: only new facts, decisions, next_actions.

---

## 3. Memory Integrity

- Entries marked `archived` or `superseded` must be ignored in retrieval.
- ContextCompiler must validate that output is **schema-compliant**.
- MCP orchestration must not alter canonical memory entries.
- Any data corruption detected should raise a **controlled exception** and be logged.

---

## 4. Token & Resource Safety

- Token budgeting is enforced to prevent **excessive memory usage**.
- Agents cannot exceed **output or context token limits**.
- Any over-budget input is trimmed by priority rules (Rules > Identity > Knowledge > Recent > Tools).

---

## 5. Agent Responsibilities

- Agents are **memory clients**, not owners.
- They must:
  - Respect retrieval rules
  - Use context_pack only
  - Do not bypass MCP for memory access
  - Log or report any anomalies safely

---

## 6. MCP Security Rules

- MCP validates:
  - Context_pack schema compliance
  - Correct retrieval backend usage
  - Safe delegation to ContextCompiler
- MCP logs all session delta write attempts
- All errors, NotImplementedError, or permission violations must return **safe fallback statuses**

---

## 7. Auditing & Logging

- Every decision and session delta must include:
  - Source reference
  - Status (pending, approved, superseded)
- Logging should **not leak sensitive data**
- Logs can be used for auditing workflow and token usage

---

## 8. Future Enhancements

- Integrate encryption for memory storage
- Role-based access control for multi-agent deployments
- Persistent audit trail for all writebacks
- Secure token validation in adapters and MCP
