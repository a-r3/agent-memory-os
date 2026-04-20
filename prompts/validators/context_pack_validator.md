# Context Pack Validation Prompt Template

Use this template when verifying a `context_pack`.

## Validation checklist
- Required keys exist exactly once.
- All packs are `list[str]`.
- `limits.max_total_tokens` and `limits.max_output_tokens` are positive integers.
- `max_output_tokens <= max_total_tokens`.
- No raw chat history or secret material appears in the pack.
