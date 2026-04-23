#!/bin/bash
# Wrapper script to run the MCP server with the virtual environment.

set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
ROOT="$( cd "$DIR/.." && pwd )"

if [ -d "$ROOT/.venv" ]; then
    source "$ROOT/.venv/bin/activate"
elif [ -d "$ROOT/venv" ]; then
    source "$ROOT/venv/bin/activate"
else
    echo "Error: no virtual environment found at $ROOT/.venv or $ROOT/venv" >&2
    echo "Run ./scripts/setup.sh to create one." >&2
    exit 1
fi

export PYTHONPATH="$ROOT/src"
python "$ROOT/src/server.py"
