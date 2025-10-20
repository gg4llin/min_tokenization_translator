# MrConductor Usage Guide

This guide walks through using the MrConductor compression stack from project bootstrap to running benchmarks and hosting the remote service.

## 1. Prerequisites

- Python 3.9 or newer
- Optional: Docker (for containerized deployment)
- Optional: Git (for cloning repositories and managing versions)

## 2. Installation

Using the provided installer:

```bash
bash install.sh          # Linux / macOS
powershell -ExecutionPolicy Bypass -File install.ps1   # Windows
```

Alternatively, install manually:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .[server,dev]
```

## 3. Bootstrapping a Session

The CLI initializes workspace directories, generates handshake keys, and emits the session packet.

```bash
PYTHONPATH=src python3 scripts/bootstrap_session.py \
  --workspace-dir ./workspace \
  --packs-dir ./workspace/packs \
  --unicode \
  --serialization
```

Output:

- `Feature Flags`: compressed payload describing enabled features.
- `Handshake Packet`: share with the remote service to negotiate capabilities.

## 4. Running Benchmarks

```bash
PYTHONPATH=src python3 scripts/run_benchmark.py --corpus path/to/corpus.txt --runs 5 --unicode --serialization
```

Metrics reported:
- Baseline token count vs. compressed
- Savings percentage
- Average and standard deviation of compression latency

## 5. Hosting the Remote Service

1. Install the `server` optional dependency.
2. Launch the FastAPI host:

```bash
PYTHONPATH=src uvicorn mrconductor.server:create_app --host 0.0.0.0 --port 8080
```

Routes include:
- `POST /handshake`: negotiate features and SSH keys.
- `POST /distill`: preprocess prompts prior to encoding.

## 6. Integration Paths

- **Custom GPT**: register the FastAPI service as an OpenAI Action.
- **MCP Server**: wrap modules as Model Context Protocol tools.
- **Direct SDK**: import `mrconductor` package inside your application to use Distiller, HandshakeManager, etc.

## 7. Troubleshooting

- Permission errors creating key directories: set `--workspace-dir` to a path you control; the installer defaults to `./workspace`.
- `ssh-keygen` missing: install OpenSSH tools (`apt install openssh-client`, `brew install openssh`, or enable through Windows Features).
- Pip install issues: ensure internet connectivity or supply wheels via local mirrors.
