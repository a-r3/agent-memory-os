# ADR-0003: Raw History Is Not Canonical Context

## Status
Approved

## Context

A common anti-pattern in agent systems is to treat chat history or raw session transcripts as the default context source.

This causes several problems:

- prompt bloat
- weak relevance
- noisy context
- rising cost
- low traceability
- difficulty separating durable facts from temporary discussion

Raw history may be useful for audit and episodic continuity, but it is not a reliable canonical context layer.

## Decision

Agent Memory OS will not treat raw chat or raw transcript history as canonical model context.

Raw history may be stored for traceability or reconstruction, but agent-facing context must be compiled from structured memory under explicit rules.

## Consequences

### Positive
- token usage becomes more controllable
- context quality improves
- durable facts can be validated separately from transcript text
- retrieval becomes more intentional

### Negative
- a context compiler becomes mandatory
- structured writeback must exist
- raw transcript convenience is intentionally reduced

## Notes

This decision protects the architecture from becoming a transcript-driven system.
