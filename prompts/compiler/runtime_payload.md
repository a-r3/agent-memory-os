# Runtime Payload Prompt Template

Use this template when building a transport-neutral runtime payload from a schema-valid `context_pack`.

## Requirements
- Preserve the canonical section ordering.
- Keep stable context cache-friendly.
- Include only compiled context, never raw transcript history.
- Surface diagnostics separately from the runtime payload.
