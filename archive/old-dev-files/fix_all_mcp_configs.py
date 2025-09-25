#!/usr/bin/env python3
import json

# Read the current Claude config
with open('/home/adam/.claude.json', 'r') as f:
    config = json.load(f)

# Navigate to the google-workspace-mcp project config
project_path = "/home/adam/Code/google-workspace-mcp"
if project_path in config["projects"]:
    project_config = config["projects"][project_path]
    
    if "mcpServers" in project_config:
        mcp_servers = project_config["mcpServers"]
        
        # Fix filesystem server
        if "filesystem" in mcp_servers:
            mcp_servers["filesystem"] = {
                "command": "npx",
                "args": [
                    "-y",
                    "@modelcontextprotocol/server-filesystem",
                    "/home/adam/Code"
                ]
            }
            print("Fixed filesystem MCP config")
        
        # Fix claude-memory server
        if "claude-memory" in mcp_servers:
            mcp_servers["claude-memory"] = {
                "command": "/home/adam/Code/claude-memory-mcp/claude-memory-mcp-venv/bin/python",
                "args": [
                    "/home/adam/Code/claude-memory-mcp/src/server_fastmcp.py"
                ]
            }
            print("Fixed claude-memory MCP config")
        
        # Fix google-calendar server
        if "google-calendar" in mcp_servers:
            mcp_servers["google-calendar"] = {
                "command": "/home/adam/Code/calendar-mcp/calendar-mcp-venv/bin/python",
                "args": [
                    "/home/adam/Code/calendar-mcp/src/server.py"
                ]
            }
            print("Fixed google-calendar MCP config")
        
        # Fix slack server
        if "slack" in mcp_servers:
            # Keep the env variables but fix the command
            env_vars = mcp_servers["slack"].get("env", {})
            mcp_servers["slack"] = {
                "command": "npx",
                "args": [
                    "-y",
                    "slack-mcp-server@latest",
                    "--transport",
                    "stdio"
                ],
                "env": env_vars
            }
            print("Fixed slack MCP config")
        
        print(f"Updated {len(mcp_servers)} MCP servers")
    else:
        print("No MCP servers found")
else:
    print(f"Project {project_path} not found in config")

# Write the updated config back
with open('/home/adam/.claude.json', 'w') as f:
    json.dump(config, f, indent=2)

print("All MCP configs updated successfully")