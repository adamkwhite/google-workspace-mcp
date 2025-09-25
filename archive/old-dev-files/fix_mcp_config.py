#!/usr/bin/env python3
import json
import sys

# Read the current Claude config
with open('/home/adam/.claude.json', 'r') as f:
    config = json.load(f)

# Navigate to the google-workspace-mcp project config
project_path = "/home/adam/Code/google-workspace-mcp"
if project_path in config["projects"]:
    project_config = config["projects"][project_path]
    
    # Fix the google-workspace MCP server config
    if "mcpServers" in project_config and "google-workspace" in project_config["mcpServers"]:
        # Change from WSL command to direct bash execution
        project_config["mcpServers"]["google-workspace"] = {
            "command": "bash",
            "args": [
                "-c",
                "cd /home/adam/Code/google-workspace-mcp && source venv/bin/activate && python src/server.py"
            ]
        }
        
        print("Fixed google-workspace MCP config")
    else:
        print("google-workspace MCP config not found")
else:
    print(f"Project {project_path} not found in config")

# Write the updated config back
with open('/home/adam/.claude.json', 'w') as f:
    json.dump(config, f, indent=2)

print("Config updated successfully")