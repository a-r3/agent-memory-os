# Scope Planning Prompt Template

Use this template to infer lightweight `memory_scope` and `repo_scope` allow-lists.

## Heuristics
- Inspect likely object kinds first.
- Reuse canonical titles, entity names, or affected module names for `repo_scope`.
- Keep scope lists small and deterministic.
- Prefer canonical memory API search results over ad hoc guessing.
