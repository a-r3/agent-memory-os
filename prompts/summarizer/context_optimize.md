# Context Optimization Prompt Template

Use this template when an existing `context_pack` needs to be compressed for a tighter budget.

## Requirements
- Preserve schema shape.
- Compress in reverse-priority order where possible.
- Keep rule and identity guidance stable when trimming lower-priority packs.
- Return budget diagnostics separately from the canonical pack.
