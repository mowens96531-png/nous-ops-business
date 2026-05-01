#!/usr/bin/env python3
"""Continuous Telegram bot for Nous Ops.
Polls for messages and responds immediately."""

import json, urllib.request, urllib.parse, time, subprocess, sys
from pathlib import Path

TOKEN = "8681348118:AAF3cz-lvP17w6s4CMRughPOagdMuMH27Ug"
CHAT = "8486989098"
BASE_URL = f"https://api.telegram.org/bot{TOKEN}"
OFFSET_FILE = Path("/tmp/telegram_offset.txt")

def get_updates(offset=None):
    """Poll Telegram for new messages."""
    params = {"limit": 10}
    if offset:
        params["offset"] = offset
    
    url = f"{BASE_URL}/getUpdates?" + urllib.parse.urlencode(params)
    try:
        with urllib.request.urlopen(url, timeout=30) as resp:
            return json.loads(resp.read())
    except Exception as e:
        print(f"Poll error: {e}")
        return {"result": []}

def send_message(text):
    """Send a message to the chat."""
    url = f"{BASE_URL}/sendMessage"
    data = urllib.parse.urlencode({"chat_id": CHAT, "text": text}).encode()
    req = urllib.request.Request(url, data=data, method="POST")
    req.add_header("Content-Type", "application/x-www-form-urlencoded")
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read())
    except Exception as e:
        print(f"Send error: {e}")
        return None

def process_command(text):
    """Process a command from the user."""
    text = text.strip().lower()
    
    if text in ["status", "/status"]:
        # Run status check
        result = subprocess.run(
            ["python3", "/Users/founderagent/workspace/nous-ops-business/scripts/status.py"],
            capture_output=True, text=True, timeout=30
        )
        return result.stdout or "Status check failed"
    
    elif text in ["scan", "/scan"]:
        # Run AutoScout
        result = subprocess.run(
            ["python3", "/Users/founderagent/workspace/nous-ops-business/products/autoscout/scanner.py"],
            capture_output=True, text=True, timeout=120
        )
        return "Scan complete. Check reports folder."
    
    elif text in ["build", "/build"]:
        return "Building latest product iteration..."
    
    elif text.startswith("deploy"):
        parts = text.split()
        if len(parts) >= 2:
            template = parts[1]
            out_dir = f"/tmp/deploy_{template}"
            result = subprocess.run(
                ["python3", "/Users/founderagent/workspace/nous-ops-business/products/agentdeploy/deploy.py", template, out_dir],
                capture_output=True, text=True, timeout=30
            )
            return result.stdout or f"Deploy initiated for {template}"
        return "Usage: deploy <template_name>"
    
    else:
        return f"Command received: {text}\n\nAvailable: status, scan, build, deploy <template>"

def main():
    offset = None
    if OFFSET_FILE.exists():
        try:
            offset = int(OFFSET_FILE.read_text().strip())
        except:
            pass
    
    print(f"[{time.strftime('%H:%M:%S')}] Bot starting... offset={offset}")
    
    while True:
        try:
            data = get_updates(offset)
            
            for update in data.get("result", []):
                offset = update["update_id"] + 1
                OFFSET_FILE.write_text(str(offset))
                
                message = update.get("message", {})
                text = message.get("text", "")
                
                if not text:
                    continue
                
                print(f"[{time.strftime('%H:%M:%S')}] Received: {text[:50]}")
                
                response = process_command(text)
                send_message(response)
                print(f"[{time.strftime('%H:%M:%S')}] Sent response")
            
            time.sleep(2)  # Poll every 2 seconds
            
        except KeyboardInterrupt:
            print("\nBot stopped")
            break
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()
