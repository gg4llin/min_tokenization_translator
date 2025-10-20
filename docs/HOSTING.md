# Hosting & Deployment Guide

This guide describes how to deploy the counterparty service that interacts with the MrConductor compression stack. It covers multiple hosting models and highlights tradeoffs so you can pick the option with the best efficacy for your workload.

## 1. FastAPI Service (Recommended)

- **Use when**: you control both endpoints and need low-latency, high-throughput exchanges.
- **How it works**: deploy the provided FastAPI app (`mrconductor.server.create_app`) behind a reverse proxy. The service exposes:
  - `POST /handshake` for feature negotiation (ASCII baseline, Unicode overlay, serialization, MCP, etc.).
  - `POST /distill` for preprocessing prompts prior to encoding.
- **Hosting**: containerize with Docker, deploy on managed Kubernetes or serverless containers (Cloud Run, App Runner). Use HTTP/2 for efficient streaming.
- **Security**: terminate TLS at the load balancer; protect endpoints with mTLS or signed JWTs. Handshake still uses SSH-key exchange for end-to-end verification.

## 2. MCP Server Integration

- **Use when**: collaborating with IDEs or tools that speak the Model Context Protocol.
- **Approach**: wrap the same module logic in an MCP tool provider. Feature flags map to MCP tool parameters; handshake occurs via a dedicated command that returns compressed exchanges.
- **Benefit**: reuses existing MCP infrastructure; easy adoption for agents that already rely on MCP.

## 3. Custom GPT (OpenAI)

- **Use when**: you want quick iteration without maintaining infrastructure.
- **Approach**: create a Custom GPT with the FastAPI service as an action (via OpenAI Actions). The GPT triggers the `/handshake` and `/distill` routes to generate compressed prompts before relaying them to the main model.
- **Tradeoff**: depends on OpenAI infrastructure and action latency; less control over caching and feature rollouts compared to self-hosted service.

## 4. Alternative Platforms

- **Serverless Functions**: workable for low-volume or bursty workloads; ensure warm-start mitigation because handshake requires generating keys and loading dictionaries.
- **Edge Runtimes**: good for geolocated latency, but validate `ssh-keygen` availability or replace with libsodium-based Ed25519 generation.

## Operational Tasks

1. **Provision secrets**: store reusable SSH keys encrypted (KMS, Vault). Rotate periodically.
2. **Dictionary sync**: replicate dynamic pack registries via shared storage (Redis, DynamoDB, etc.).
3. **Monitoring**: export token savings, latency, and error metrics; alert when savings drop below target thresholds.
4. **Benchmarking**: schedule benchmark runs (scripts/run_benchmark.py) with representative corpora to detect regressions.
5. **Auditing**: keep decoded audit trails for compliance; ensure logs redact sensitive fields.

By default, start with the FastAPI deployment for controllable, high-efficiency hosting. Layer in Custom GPT or MCP integrations as complementary access channels depending on your product surface area.
