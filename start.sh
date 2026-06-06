#!/usr/bin/env bash
#
# Start the Jupyter AI (v3) environment.
#
# Chat is served by the Jupyternaut agent; pick the model in Jupyternaut
# Settings and @-mention @Jupyternaut in a chat.
#
# Backend: Ollama (local, default) or OpenRouter (hosted). Ollama is required
# unless OPENROUTER_API_KEY is set, in which case a missing Ollama server is a
# warning rather than an error (so you can run OpenRouter-only).
#
# Steps performed:
#   1. Check the Ollama server (fatal unless OPENROUTER_API_KEY is set).
#   2. Activate the local virtualenv (creating/installing it if missing).
#   3. Launch JupyterLab with the Jupyter AI chat enabled.
#
set -euo pipefail
cd "$(dirname "$0")"

OLLAMA_HOST_URL="${OLLAMA_HOST:-http://127.0.0.1:11434}"

# 1. Is Ollama running?
if curl -sf "${OLLAMA_HOST_URL}/api/tags" >/dev/null 2>&1; then
  OLLAMA_UP=1
else
  OLLAMA_UP=0
  if [ -n "${OPENROUTER_API_KEY:-}" ]; then
    echo "WARNING: Ollama not reachable at ${OLLAMA_HOST_URL}, but OPENROUTER_API_KEY is set."
    echo "         Continuing for OpenRouter use (local Ollama models will be unavailable)."
  else
    echo "ERROR: Ollama server not reachable at ${OLLAMA_HOST_URL}"
    echo "Start it with 'ollama serve', or set OPENROUTER_API_KEY to use OpenRouter instead."
    exit 1
  fi
fi

# 2. Ensure the virtualenv exists and its dependencies are in sync.
if [ ! -d .venv ]; then
  echo "Creating virtualenv (first run)..."
  python3 -m venv .venv
  .venv/bin/python -m pip install --upgrade pip
fi

# (Re)install deps whenever requirements.txt is newer than the last install.
# Installing only on venv creation would mean dependencies ADDED to
# requirements.txt later silently never land in an existing .venv. The stamp
# makes start.sh idempotent and self-healing while staying fast on unchanged runs.
REQ_STAMP=.venv/.requirements-installed
if [ ! -f "$REQ_STAMP" ] || [ requirements.txt -nt "$REQ_STAMP" ]; then
  echo "Installing/updating dependencies from requirements.txt..."
  .venv/bin/python -m pip install -r requirements.txt
  touch "$REQ_STAMP"
fi

# Pin the Jupyter kernelspec to THIS venv's interpreter (absolute path).
# ipykernel ships a default kernelspec whose argv[0] is the bare string "python"
# (PATH-relative). jupyter_client usually substitutes the server interpreter, but
# that behavior is version-dependent: on a machine where bare `python` resolves to
# another interpreter (e.g. /opt/anaconda3/bin/python), notebooks would silently
# run OUTSIDE this venv and miss its deps (pandas/numpy/matplotlib). Rewriting the
# spec via `ipykernel install` pins argv[0] to .venv/bin/python deterministically.
# Self-healing: re-pins whenever the spec is missing or not already absolute.
KERNEL_JSON=.venv/share/jupyter/kernels/python3/kernel.json
VENV_PY="${PWD}/.venv/bin/python"
if [ ! -f "$KERNEL_JSON" ] || ! grep -q "$VENV_PY" "$KERNEL_JSON"; then
  echo "Pinning Jupyter kernelspec to the venv interpreter..."
  .venv/bin/python -m ipykernel install --sys-prefix --name python3 \
    --display-name "Python 3 (.venv)" >/dev/null 2>&1
fi

# Jupyter AI v3 ships no model agent by default; the Ollama/OpenRouter chat needs
# the optional Jupyternaut agent (the [jupyternaut] extra). Warn if it's missing.
if ! .venv/bin/python -c "import jupyter_ai_jupyternaut" >/dev/null 2>&1; then
  echo "WARNING: the Jupyternaut agent isn't installed in .venv, so @Jupyternaut"
  echo "         won't appear in chats. Reinstall deps: .venv/bin/python -m pip install -r requirements.txt"
fi

# 3. Launch JupyterLab.
# DEFAULT_MODEL is the default *Ollama* model (only used for the message + check
# below). The model Jupyter AI actually loads comes from Jupyternaut Settings,
# saved in ~/.../jupyter_ai/config.json — OpenRouter models are selected there too.
DEFAULT_MODEL="gemma4:26b-mlx"
if [ "$OLLAMA_UP" -eq 1 ]; then
  echo "Ollama OK at ${OLLAMA_HOST_URL}. Default Ollama model for this repo: ${DEFAULT_MODEL}"
  echo "Available models:"
  ollama list || true
  if ! ollama list 2>/dev/null | grep -q "${DEFAULT_MODEL}"; then
    echo "NOTE: default model '${DEFAULT_MODEL}' not pulled yet. Run: ollama pull ${DEFAULT_MODEL}"
  fi
fi
echo
echo "Tip: open a chat from the launcher (Chat card) and @-mention @Jupyternaut,"
echo "     or @-mention @Tutor for the built-in Python tutor persona."
echo "     Pick the model in Settings -> Jupyternaut Settings (e.g. ollama/${DEFAULT_MODEL})."
echo
# --config applies jupyter_ai_config.py (e.g. the ollama/gemma4:26b-mlx num_ctx cap).
exec .venv/bin/jupyter lab --config="${PWD}/jupyter_ai_config.py" "$@"
