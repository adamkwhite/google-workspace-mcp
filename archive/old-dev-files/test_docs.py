#!/usr/bin/env python3
"""Test creating a Google Doc via the MCP server."""

import json
import subprocess
import sys

def test_create_doc():
    """Test creating a Google Doc through the MCP server."""
    
    cmd = [sys.executable, "src/server.py"]
    proc = subprocess.Popen(
        cmd,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    try:
        # Build the complete MCP protocol sequence
        messages = []
        
        # 1. Initialize
        messages.append({
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "clientInfo": {"name": "test-client", "version": "1.0.0"}
            }
        })
        
        # 2. Initialized notification
        messages.append({
            "jsonrpc": "2.0",
            "method": "notifications/initialized"
        })
        
        # 3. Create Google Doc
        messages.append({
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "create_google_doc",
                "arguments": {
                    "title": "Test Document from MCP",
                    "content": "This is a test document created via the Google Workspace MCP server.\n\nIt should be created in the designated Claude MCP Documents folder."
                }
            }
        })
        
        # Convert to newline-separated JSON
        input_data = "\n".join(json.dumps(msg) for msg in messages) + "\n"
        
        print("Creating test Google Doc...")
        
        stdout, stderr = proc.communicate(input=input_data, timeout=30)
        
        print("\n=== RESPONSES ===")
        if stdout:
            lines = stdout.strip().split('\n')
            for i, line in enumerate(lines):
                if line.strip():
                    try:
                        response = json.loads(line)
                        if response.get("id") == 3:  # Doc creation response
                            print(f"Document creation result:")
                            print(json.dumps(response, indent=2))
                        else:
                            print(f"Response {i+1}: {response.get('method', response.get('id', 'unknown'))}")
                    except json.JSONDecodeError:
                        print(f"Invalid JSON: {line}")
        
        print(f"\n=== LOGS ===")
        if stderr:
            print(stderr)
        
        print(f"\nReturn code: {proc.returncode}")
        
    except subprocess.TimeoutExpired:
        proc.kill()
        stdout, stderr = proc.communicate()
        print("Timeout!")
        print("STDERR:", stderr)

if __name__ == "__main__":
    print("Testing Google Doc creation via MCP...")
    test_create_doc()