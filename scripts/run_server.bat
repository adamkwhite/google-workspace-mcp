@echo off
REM Wrapper script to run the MCP server with the virtual environment in WSL

cd /d "%~dp0"
wsl bash -c "cd /home/adam/Code/google-workspace-mcp && source venv/bin/activate && python src/server.py"