# ADR-0005: Important Facts Require Source and Status

## Status
Approved

## Context

A memory system that stores facts without traceability will eventually become unreliable.

If all stored information is treated equally, the system cannot distinguish between:

- speculation
- draft notes
- agent assumptions
- verified findings
- approved durable truth
- superseded information

That creates a serious quality and governance problem.

## Decision

Important memory entries in Agent Memory OS must carry source and status.

At minimum, the system should distinguish between:

- draft
- unverified
- verified
- approved
- superseded
- archived

Where applicable, important facts should include source references and confidence signals.

## Consequences

### Positive
- traceability improves
- retrieval quality can improve
- governance becomes possible
- weak or noisy memory can be separated from trusted memory

### Negative
- writeback becomes more structured
- some user convenience is traded for higher quality
- source handling must be maintained consistently

## Notes

This decision is required to prevent memory drift and self-reinforcing hallucinated knowledge.
