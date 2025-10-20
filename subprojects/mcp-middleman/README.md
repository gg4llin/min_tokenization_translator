# MCP Middleman Subproject

This subproject explores an intermediary MCP server that manages handshake negotiation, dictionary caching, and domain-specific tuning before relaying payloads to the main MrConductor compression stack.

## Objectives

- Prototype an MCP server that exposes the distillation and encoding pipeline as MCP tools.
- Evaluate benefits of inserting a specialized agent for domain-tailored pack management.
- Maintain focus on core prototype first; complex infrastructure (orchestration, autoscaling) will follow later phases.

## Directory Layout

- `docs/` — Planning notes and integration guides.
- `src/` — MCP server implementation (to be added once prototype begins).
- `experiments/` — Scripts for testing agent behaviors and pack strategies.

## Status

- Documentation placeholders seeded.
- Awaiting prototype design sign-off before coding.
