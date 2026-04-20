# ADR-0004: Context Must Be Compiled Under a Strict Budget

## Status
Approved

## Context

Even a well-structured memory system can fail if context assembly is undisciplined.

If relevant memory is simply appended until the prompt is large, then:

- token costs rise
- context becomes noisy
- model performance may degrade
- stable memory scales badly with time

A central mechanism is needed to decide what enters context and what stays retrievable but out of prompt.

## Decision

All agent-facing context in Agent Memory OS must be compiled under an explicit budget.

The Context Compiler is responsible for selecting, compressing, ranking, and packaging only the smallest useful context for a given task.

## Consequences

### Positive
- token usage becomes controllable
- compact context becomes the default
- stable memory can grow without forcing prompt growth
- retrieval and compression become first-class concerns

### Negative
- the compiler becomes a critical system component
- poor ranking or compression could hide useful information
- budget policy must be maintained over time

## Notes

The context budget is not only a cost control mechanism.  
It is a design constraint that shapes the whole system.
