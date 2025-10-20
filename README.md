# MrConductor Compression Stack

Modular tooling for building and benchmarking compact machine-to-machine prompt exchanges. It implements the compressed protocol defined in `prompt.md`, adds feature flag negotiation, secure handshakes, bootstrap utilities, and benchmarking harnesses that compare savings versus standard prompting.

## Repository Layout

- `prompt.md` — primary specification for the compressed language, workflows, and design notes.
- `src/mrconductor/` — Python package housing configuration, handshake, bootstrap, and benchmarking modules.
- `scripts/` — command-line entry points.
- `docs/` — architecture and protocol references.
- `tests/` — regression and contract tests.

## Quick Start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
python scripts/bootstrap_session.py --help
python scripts/run_benchmark.py --help
```

## Features

- Feature flag negotiation to toggle ASCII baseline, Unicode overlay, serialization, and adaptive packs.
- Secure session handshake using ephemeral or reusable SSH keys.
- Bootstrap CLI for provisioning dictionaries, pack registries, and transport adapters.
- Benchmark harness to compare token consumption and latency against standard prompting.
- Optional FastAPI host (`scripts/run_server.py`) exposing handshake and distillation endpoints for remote agents or Custom GPT tooling.

## Security Considerations

- Defaults to per-session Ed25519 keys; reuse is opt-in and stored encrypted at rest.
- Authenticated handshake negotiates protocol versions, tokenizer fingerprints, and feature capabilities.
- All serialized payloads include checksums prior to ASCII symbol encoding.

See `docs/ARCHITECTURE.md` for deeper module design and integration guidance.
Consult `docs/USAGE.md` for day-to-day workflows and `docs/HOSTING.md` for deployment options.
Deployment steps are outlined in `docs/DEPLOYMENT.md`, and GitHub publication guidance lives in `docs/GITHUB_SETUP.md`.

## Virtual Testing

Run the light regression suite to validate feature flags, handshake packets, and benchmark scaffolding without invoking external services:

```bash
pytest
```

## Installation Scripts

- Linux/macOS: `bash installers/install.sh [-v]`
- Windows: `powershell -ExecutionPolicy Bypass -File installers/install.ps1 [-VerboseMode]`

Verbose flags stream progress in real time. Both installers create a virtualenv, install dependencies, build the optional Docker image (if available), and drop CLI wrappers into `.mrconductor/bin/`.
