# Agent Memory OS — Agents Guide

This document describes the behavior rules and integration principles for agents in Agent Memory OS.

---

## 1. Agents Overview

Agents act as **memory clients** in the system.  
No agent owns memory. All agents:

- read from memory
- receive compact context for queries
- write only structured deltas
- register decisions and outcomes

The Memory OS brain is the shared center.  
This applies to Codex, Claude/Cloud, and other agents alike.

---

## 2. Core Principles for Agents

1. **Memory is canonical**  
   Structured memory is always the authoritative source.

2. **No raw history in context**  
   Raw chat or full transcript is never injected directly into agent prompts.

3. **Use compiled context only**  
   Agents receive only **Context Compiler** generated compact context.

4. **Delta-based writeback**  
   Session results are written back as deltas.

5. **Decision registration**  
   Decisions must be separately registered.

6. **Source and status**  
   Each fact, rule, or decision must have `source` and `status`.

7. **Token budget adherence**  
   Context Compiler token limits must always be respected.

---

## 3. Workflow for Agents

1. **Fetch context**  
   - Query `context_pack` via MCP.
   - Compiler returns the relevant memory.

2. **Execute task**  
   - Agent performs the task using compact context.
   - Input and tools are used as needed.

3. **Writeback session delta**  
   - New facts, changes, decisions, and artifacts are written as session delta.
   - Any new decisions are also registered in the decision registry.

4. **Maintain traceability**  
   - Every entry has `source` and `status`.
   - Duplicates and obsolete information are managed systematically.

---

## 4. Forbidden Practices

- Injecting raw chat or full transcript into prompts  
- Writing unverified facts as verified  
- Storing secrets, PII, or sensitive material openly in memory  
- Creating duplicate entries without canonical linking  
- Expanding memory client role arbitrarily

---

## 5. Agent Types (Initial Support)

| Agent | Role | Notes |
|-------|------|-------|
| Codex | Code analysis, generation | Uses context_pack, writes deltas |
| Claude / Cloud | Planning, summarization | Uses context_pack, writes deltas |
| Generic Adapter | Future agents | Contract for read/write via MCP, delta writeback |

---

## 6. Integration Notes

- Agents access memory API and tools via MCP.  
- Adapter layers should remain minimal.  
- Adapters handle only:
  - context_pack request
  - output formatting
  - writeback hook  
- Adapters must be replacement-friendly.

---

## 7. Best Practices

- Always validate retrieved context before executing critical tasks.  
- Promote only verified or approved items to long-term memory.  
- Keep session deltas concise and structured.  
- Respect token budgets; avoid unnecessary context inflation.  
- Register decisions for significant architectural or workflow changes.  
- Track agent actions for audit and traceability.

---

## 8. Immediate Next Steps for Agents

- Implement minimal Codex adapter (compile → execute → writeback).  
- Implement minimal Claude adapter (compile → execute → writeback).  
- Test delta writeback and decision registration workflows.  
- Validate token budgeting and context compression.  
- Ensure traceability with source/status fields.

---

This document precisely defines how all agents operate, which rules they must follow, and how writeback principles work in Agent Memory OS.
