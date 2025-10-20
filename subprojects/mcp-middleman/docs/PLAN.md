# MCP Middleman Plan

## Scope

- Build a lightweight MCP server that proxies the MrConductor pipeline.
- Allow the server to maintain session lexicons and feature flags across clients.
- Explore optional embedded domain agent for adaptive pack recommendations.

## Phases

1. Prototype
    - Scaffold MCP server interfaces without heavy infra.
    - Reuse existing distiller/encoder modules via dependency injection.
    - Provide manual trigger scripts in `experiments/` to simulate clients.
2. Integration
    - Add authentication, caching, and logging.
    - Evaluate agent enhancements (pattern tuning, pack rotation).
3. Production Hardening
    - Dockerize, add monitoring, and define autoscaling hooks.

## Open Questions

- Which MCP clients will we target first (Cursor, Cline, etc.)?
- How will session state persist across restarts (local storage vs. Redis)?
- What agent frameworks best fit the adaptive pack use case?
