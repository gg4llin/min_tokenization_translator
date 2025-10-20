#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
ROOT_DIR=$(cd "${SCRIPT_DIR}/.." && pwd)
cd "${ROOT_DIR}"

VERBOSE=false
while getopts "vh" opt; do
  case "$opt" in
    v) VERBOSE=true ;;
    h)
      cat <<'USAGE'
Usage: install.sh [-v]

Options:
  -v    Verbose output (show progress messages and command output)
  -h    Show this help text
USAGE
      exit 0
      ;;
  esac
done
shift $((OPTIND - 1))

log() {
  if [ "$VERBOSE" = true ]; then
    echo "[install] $1"
  fi
}

run_cmd() {
  if [ "$VERBOSE" = true ]; then
    eval "$@"
  else
    eval "$@" >/dev/null 2>&1
  fi
}

ensure_command() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "Error: required command '$1' not found." >&2
    exit 1
  fi
}

ensure_command python3

log "Detected root directory ${ROOT_DIR}"

PREFIX="${ROOT_DIR}/.min_tokenization_translator"
mkdir -p "${PREFIX}/bin"
log "Using installation prefix ${PREFIX}"

if [ ! -d .venv ]; then
  log "Creating virtual environment"
  run_cmd "python3 -m venv .venv"
else
  log "Virtual environment already exists"
fi

VENV_PYTHON="${ROOT_DIR}/.venv/bin/python"
VENV_PIP="${ROOT_DIR}/.venv/bin/pip"

log "Upgrading pip"
if [ "$VERBOSE" = true ]; then
  "${VENV_PIP}" install --upgrade pip
else
  "${VENV_PIP}" install --upgrade pip >/dev/null
fi

log "Installing project dependencies"
if [ "$VERBOSE" = true ]; then
  "${VENV_PIP}" install -e .[server,dev]
else
  "${VENV_PIP}" install -q -e .[server,dev]
fi

create_wrapper() {
  local name="$1"
  local target="$2"
  cat <<EOT > "${PREFIX}/bin/${name}"
#!/usr/bin/env bash
ROOT_DIR="${ROOT_DIR}"
source "\${ROOT_DIR}/.venv/bin/activate"
PYTHONPATH="\${ROOT_DIR}/src" "\${ROOT_DIR}/scripts/${target}" "\$@"
EOT
  chmod +x "${PREFIX}/bin/${name}"
}

log "Installing CLI wrappers"
create_wrapper "mtt-bootstrap" "bootstrap_session.py"
create_wrapper "mtt-benchmark" "run_benchmark.py"

if command -v docker >/dev/null 2>&1; then
  log "Building Docker image (min-tokenization-translator:latest)"
  if [ "$VERBOSE" = true ]; then
    docker build -t min-tokenization-translator:latest "${ROOT_DIR}"
  else
    docker build -q -t min-tokenization-translator:latest "${ROOT_DIR}" >/dev/null
  fi
else
  log "Docker not available; skipping image build"
fi

cat <<SUMMARY
Installation complete.
Add ${PREFIX}/bin to your PATH, e.g.:
  export PATH=\$PATH:${PREFIX}/bin

Available commands:
  mtt-bootstrap
  mtt-benchmark
SUMMARY
