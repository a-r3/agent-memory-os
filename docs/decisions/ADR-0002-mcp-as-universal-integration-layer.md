# ADR-0002: MCP as Universal Integration Layer

## Status
Approved

## Context

The system must expose memory capabilities to different agent environments and toolchains.

A vendor-specific or agent-specific integration path would produce unnecessary fragmentation and coupling.

The integration layer needs to support at least:

- tools
- resources
- reusable prompts
- future portability across agent ecosystems

## Decision

Agent Memory OS will expose its primary external integration surface through MCP.

## Consequences

### Positive
- integration becomes standardized
- tools, resources, and prompts can be organized cleanly
- multiple agent runtimes can access the same memory substrate
- portability improves

### Negative
- MCP contracts must be designed carefully
- the system must still support internal APIs as needed
- adapter layers remain necessary for some agent-specific behavior

## Notes

MCP is not the memory model itself.  
It is the standard way external agents interact with the memory model.
