# MrConductor TODO

## High Priority
- [ ] Implement real tokenizer integration in `BenchmarkRunner` and replace placeholder compression logic.
- [ ] Add encode/decode endpoints to `mrconductor.server` for end-to-end payload exchange.
- [ ] Encrypt reusable SSH keys at rest and document rotation procedures.
- [ ] Build integration tests covering Unicode overlay and serialization flag combinations.

## Medium Priority
- [ ] Port PromptDistiller heuristics to domain-specific plugins (e.g., medical, finance).
- [ ] Provide Docker Compose examples for multi-service deployments (FastAPI + Redis pack store).
- [ ] Enhance CLI to export pack manifests and import them into remote hosts.
- [ ] Add optional telemetry hooks for reporting savings to APM platforms.

## Low Priority
- [ ] Explore streaming compression (chunked pack updates during long sessions).
- [ ] Investigate WebSocket transport and HTTP/2 multiplexing for low-latency pipelines.
- [ ] Publish sample corpora and benchmark reports in `docs/samples/`.
