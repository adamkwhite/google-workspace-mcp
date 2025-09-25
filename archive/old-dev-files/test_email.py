#!/usr/bin/env python3
"""Test sending an email via the MCP server."""

import json
import subprocess
import sys

def test_send_email():
    """Test sending an email through the MCP server."""
    
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
        
        # 3. Send email tool call
        messages.append({
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "send_email",
                "arguments": {
                    "to": "adamkwhite@gmail.com",
                    "subject": "Test Email from MCP Server",
                    "body": "Hello! This is a test email sent via the Google Workspace MCP server.",
                    "html": False
                }
            }
        })
        
        # Convert to newline-separated JSON
        input_data = "\n".join(json.dumps(msg) for msg in messages) + "\n"
        
        print("Sending email test...")
        print("Note: Replace 'your-email@example.com' with your actual email address")
        
        stdout, stderr = proc.communicate(input=input_data, timeout=30)
        
        print("\n=== RESPONSES ===")
        if stdout:
            lines = stdout.strip().split('\n')
            for i, line in enumerate(lines):
                if line.strip():
                    try:
                        response = json.loads(line)
                        if response.get("id") == 3:  # Email response
                            print(f"Email result: {json.dumps(response, indent=2)}")
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
        print("Timeout! Check if authentication is required.")
        print("STDERR:", stderr)

if __name__ == "__main__":
    print("Testing email sending via MCP...")
    print("Make sure to:")
    print("1. Replace the email address in the script")
    print("2. Have valid Google credentials configured")
    print("3. Be ready for OAuth browser popup if needed")
    print()
    
    test_send_email()