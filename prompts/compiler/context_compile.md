# Context Compiler Prompt Template

Use this template when a caller wants a compact `context_pack` under a token budget.

## Inputs
- `agent`
- `task`
- `budget_tokens`
- `memory_scope`
- `repo_scope`

## Requirements
- Use compiled context only.
- Do not include raw chat or transcript history.
- Preserve `rules_pack`, `identity_pack`, `knowledge_pack`, `recent_pack`, `tools_pack`, and `limits`.
- Respect token budgeting and favor stable reusable context first.
