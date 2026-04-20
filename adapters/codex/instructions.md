# Codex Adapter Instructions

Codex is a memory client.

## Workflow
1. Request `context_pack` through MCP.
2. Optionally inspect `context_diagnostics` and `runtime_payload`.
3. Execute the task.
4. Write back structured `session_delta`.
5. Register decisions separately.

## Rules
- Do not inject raw chat into prompts.
- Do not bypass MCP for memory access.
- Respect token budgets and schema-shaped context.
