#!/bin/bash
# Wrapper script to run the MCP server with the virtual environment

# Get the directory where this script is located
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Activate the virtual environment
source "$DIR/venv/bin/activate"

# Run the server
python "$DIR/src/server.py"