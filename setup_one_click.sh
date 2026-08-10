#!/usr/bin/env bash
set -euo pipefail

# One-click setup script for AI College (Ollama + Python + Node)
# Usage: ./setup_one_click.sh [-y|--yes] [--serve]
#  -y/--yes : auto-accept prompts and install missing prerequisites automatically
#  --serve  : start `ollama serve` in the background after pulling the model

ROOT="$(cd "$(dirname "$0")" && pwd)"
BACKEND_DIR="$ROOT/backend"
FRONTEND_DIR="$ROOT/frontend"
VENV_DIR="$BACKEND_DIR/.venv"
SCRIPT_NAME="$(basename "$0")"

YES=false
START_SERVE=false

print_help() {
  cat <<EOF
Usage: $SCRIPT_NAME [-y|--yes] [--serve]

One-click setup to:
 - create a Python virtualenv and install backend requirements
 - install Node dependencies in frontend
 - create .env from .env.example if needed
 - install Ollama (optional) and pull the configured Ollama model

Flags:
 -y, --yes   Auto-accept prompts and install missing prerequisites automatically
 --serve     Start 'ollama serve' in the background after pulling the model
EOF
}

while [[ ${#} -gt 0 ]]; do
  case "$1" in
    -y|--yes)
      YES=true; shift ;;
    --serve)
      START_SERVE=true; shift ;;
    -h|--help)
      print_help; exit 0 ;;
    *)
      echo "Unknown arg: $1"; print_help; exit 2 ;;
  esac
done

info() { echo -e "\033[1;34m[INFO]\033[0m $*"; }
warn() { echo -e "\033[1;33m[WARN]\033[0m $*"; }
err() { echo -e "\033[1;31m[ERROR]\033[0m $*"; exit 1; }

has_sudo() { command -v sudo >/dev/null 2>&1; }

run_privileged() {
  if [[ $EUID -eq 0 ]]; then
    "$@"
  elif has_sudo; then
    sudo "$@"
  else
    err "Administrator privileges are required to install system packages. Please run this script with sudo or install the missing tools manually."
  fi
}

detect_os() {
  if [[ -f /etc/os-release ]]; then
    # shellcheck disable=SC1091
    . /etc/os-release
    local os_id="${ID:-}"
    local os_like="${ID_LIKE:-}"

    case "$os_id" in
      ubuntu|debian)
        echo "debian"
        ;;
      fedora|rhel|centos|rocky)
        echo "fedora"
        ;;
      arch|manjaro)
        echo "arch"
        ;;
      *)
        if [[ "$os_like" =~ (debian|ubuntu) ]]; then
          echo "debian"
        elif [[ "$os_like" =~ (fedora|rhel) ]]; then
          echo "fedora"
        elif [[ "$os_like" =~ arch ]]; then
          echo "arch"
        else
          echo "unknown"
        fi
        ;;
    esac
  else
    echo "unknown"
  fi
}

install_prereqs() {
  local distro="$1"
  info "Installing missing system prerequisites..."
  case "$distro" in
    debian)
      run_privileged apt-get update
      run_privileged apt-get install -y python3 python3-venv python3-pip curl nodejs npm
      ;;
    fedora)
      if command -v dnf >/dev/null 2>&1; then
        run_privileged dnf install -y python3 python3-pip python3-virtualenv curl nodejs npm
      elif command -v yum >/dev/null 2>&1; then
        run_privileged yum install -y python3 python3-pip python3-virtualenv curl nodejs npm
      else
        err "No supported package manager found for Fedora/RHEL-based systems."
      fi
      ;;
    arch)
      run_privileged pacman -Syu --noconfirm python python-pip curl nodejs npm
      ;;
    *)
      err "Unsupported OS. Please install python3, python3-venv, nodejs, npm, and curl manually, then rerun this script."
      ;;
  esac
}

ensure_prereqs() {
  local distro
  distro="$(detect_os)"

  if command -v python3 >/dev/null 2>&1 && python3 -m venv --help >/dev/null 2>&1 && command -v node >/dev/null 2>&1 && command -v npm >/dev/null 2>&1 && command -v curl >/dev/null 2>&1; then
    return 0
  fi

  if [[ "$YES" == "true" ]]; then
    install_prereqs "$distro"
  else
    echo
    warn "One or more required tools are missing: python3, python3-venv, node, npm, or curl."
    read -r -p "Install the required system packages now? [y/N]: " answer
    answer="${answer:-N}"
    if [[ "$answer" =~ ^[Yy]$ ]]; then
      install_prereqs "$distro"
    else
      err "Please install the required tools manually and rerun this script."
    fi
  fi
}

# Ensure required directories exist
if [[ ! -d "$BACKEND_DIR" ]]; then
  err "Backend directory not found at $BACKEND_DIR"
fi
if [[ ! -d "$FRONTEND_DIR" ]]; then
  err "Frontend directory not found at $FRONTEND_DIR"
fi

ensure_prereqs

if [[ ! -f "$ROOT/.env" ]]; then
  cp "$ROOT/.env.example" "$ROOT/.env"
  info "Created $ROOT/.env from .env.example"
fi

# Determine model from .env or .env.example
MODEL=""
if [[ -f "$ROOT/.env" ]]; then
  MODEL_LINE=$(grep -E '^\s*OLLAMA_MODEL=' "$ROOT/.env" || true)
fi
if [[ -z "${MODEL_LINE:-}" && -f "$ROOT/.env.example" ]]; then
  MODEL_LINE=$(grep -E '^\s*OLLAMA_MODEL=' "$ROOT/.env.example" || true)
fi
if [[ -n "${MODEL_LINE:-}" ]]; then
  MODEL=${MODEL_LINE#*=}
  MODEL=${MODEL//\"/}
  MODEL=${MODEL//\'/}
  MODEL=${MODEL//[[:space:]]/}
fi
if [[ -z "$MODEL" ]]; then
  MODEL="qwen2.5:1.5b"
fi

info "Using Ollama model: $MODEL"

info "Setting up Python virtualenv at $VENV_DIR and installing backend requirements"
if [[ ! -d "$VENV_DIR" ]]; then
  python3 -m venv "$VENV_DIR"
else
  info "Virtualenv already exists at $VENV_DIR"
fi
# shellcheck source=/dev/null
source "$VENV_DIR/bin/activate"
python -m pip install --upgrade pip setuptools wheel
REQ_FILE="$BACKEND_DIR/requirements.txt"
if [[ -f "$REQ_FILE" ]]; then
  pip install --upgrade --no-cache-dir -r "$REQ_FILE"
else
  warn "No requirements.txt found at $REQ_FILE — skipping Python dependency installation"
fi

info "Installing Node dependencies in $FRONTEND_DIR"
(
  cd "$FRONTEND_DIR"
  if [[ -f "package-lock.json" ]]; then
    npm ci
  else
    npm install
  fi
)

install_ollama() {
  info "Installing Ollama via the official install script..."
  curl -fsSL https://ollama.com/install.sh | sh
}

if ! command -v ollama >/dev/null 2>&1; then
  if [[ "$YES" == "true" ]]; then
    install_ollama
  else
    echo
    warn "Ollama CLI not found on PATH."
    read -r -p "Install Ollama now using the official install script? [y/N]: " yn
    yn=${yn:-N}
    if [[ "$yn" =~ ^[Yy]$ ]]; then
      install_ollama
    else
      warn "Skipping Ollama installation. The rest of the setup will continue but Ollama model pull will fail until Ollama is installed."
    fi
  fi
fi

if command -v ollama >/dev/null 2>&1; then
  info "Ollama is installed: $(ollama --version 2>/dev/null || echo 'unknown version')"
  info "Checking for model $MODEL"
  if ollama list 2>/dev/null | grep -Fq "$MODEL"; then
    info "Model $MODEL already present"
  else
    info "Pulling model $MODEL (this may take a while depending on model size and network)"
    ollama pull "$MODEL"
  fi

  if [[ "$START_SERVE" == true ]]; then
    info "Starting 'ollama serve' in background; logs -> $ROOT/ollama-serve.log"
    nohup ollama serve >"$ROOT/ollama-serve.log" 2>&1 &
    sleep 1
    if ps aux | grep -v grep | grep -q "ollama serve"; then
      info "Ollama serve started successfully (see $ROOT/ollama-serve.log)."
    else
      warn "Failed to detect an 'ollama serve' process. Check $ROOT/ollama-serve.log for details. You can start it manually with: ollama serve"
    fi
  else
    info "Ollama serve not started. To run the server: ollama serve"
  fi
else
  warn "Ollama not installed; skipping model pull. Install Ollama and run: ollama pull $MODEL"
fi

cat <<EOF

SETUP COMPLETE

Backend virtualenv: $VENV_DIR (activate with: source $VENV_DIR/bin/activate)
Frontend: installed node dependencies under $FRONTEND_DIR
Environment file: $ROOT/.env
Ollama model: $MODEL

Next steps:
 - Start the backend:
    source $VENV_DIR/bin/activate
    cd backend
    uvicorn app.main:app --reload --port 8000
 - Start the frontend:
    cd frontend
    npm run dev
 - Start Ollama if needed:
    ollama serve

If you want to start Ollama automatically every time, run:
  ./$SCRIPT_NAME --serve

EOF
