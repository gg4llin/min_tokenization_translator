# Deployment Guide

This guide describes how to deploy the Min Tokenization Translator compression stack in different environments and prepare supporting infrastructure.

## 1. Prerequisites

- Python 3.9+
- `ssh-keygen` (OpenSSH client tools)
- Optional: Docker and Docker Compose
- Optional: Git (for repository management)

## 2. Local Deployment (Linux/macOS)

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .[server]
uvicorn min_tokenization_translator.server:create_app --host 0.0.0.0 --port 8080
```

### Windows

```powershell
python -m venv .venv
. .\.venv\Scripts\Activate.ps1
pip install -e .[server]
uvicorn min_tokenization_translator.server:create_app --host 0.0.0.0 --port 8080
```

### Verify

```bash
curl -X POST http://localhost:8080/handshake -H "Content-Type: application/json" -d '{"allow_reusable_keys": false}'
```

## 3. Docker Deployment

1. Build image:
   ```bash
   docker build -t min-tokenization-translator:latest .
   ```
2. Run container:
   ```bash
   docker run -p 8080:8080 --name min-tokenization-translator min-tokenization-translator:latest
   ```
3. Use environment variables for logging, security, or to mount pack directories (`-v /data/packs:/app/workspace/packs`).

## 4. Production Considerations

- **TLS**: Terminate TLS at a reverse proxy (nginx, Traefik, AWS ALB). Route traffic to the FastAPI app.
- **State**: Persist pack registries and reusable keys under a secure volume or external data store.
- **Scaling**: Front with a load balancer; enable horizontal scaling by sharing pack caches (Redis, DynamoDB).
- **Monitoring**: Export metrics (token savings, latency) to Prometheus or CloudWatch. Enable structured logging.

## 5. Optional Integrations

- **Custom GPT / Actions**: Expose `/handshake` and `/distill` endpoints over HTTPS with OAuth. Configure the Action schema to invoke these endpoints before delegating to the core model.
- **Assistants API Tool**: Register the same endpoints as tools; add validation to ensure feature flags align with assistant capabilities.
- **MCP Middleman (future)**: Consult `subprojects/mcp-middleman/` for a proxy that manages lexicon caching and agent tuning.

## 6. CI/CD Pipeline Outline

- Lint & test (`python3 -m py_compile`, `pytest`).
- Build Docker image and run container smoke tests.
- Push artifact to registry (GHCR, ECR).
- Deploy via infrastructure-as-code (Terraform, CloudFormation) or container platform (Kubernetes, ECS).

## 7. Rollback Strategy

- Keep previous Docker images tagged (e.g., `min-tokenization-translator:previous`).
- Store pack registries with version metadata to support downgrade.
- Maintain infrastructure templates for quick redeploy of last-known-good state.

## 8. Security Checklist

- Rotate SSH keys used for handshake and store encrypted.
- Enforce authentication (API keys, OAuth, mTLS).
- Sanitize logs to avoid leaking prompt contents.
- Run vulnerability scans on Docker images.
