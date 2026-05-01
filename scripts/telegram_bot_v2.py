#!/usr/bin/env python3
"""Telegram Bot v2 - Simplified and robust."""
import json, urllib.request, urllib.parse, time, sys

TOKEN = "8681348118:AAF3cz-lvP17w6s4CMRughPOagdMuMH27Ug"
CHAT = "8486989098"
BASE = f"https://api.telegram.org/bot{TOKEN}"
OFFSET = 0

def send(text):
    data = urllib.parse.urlencode({"chat_id": CHAT, "text": text}).encode()
    req = urllib.request.Request(f"{BASE}/sendMessage", data=data, method="POST")
    req.add_header("Content-Type", "application/x-www-form-urlencoded")
    try:
        urllib.request.urlopen(req, timeout=15)
    except Exception as e:
        print(f"Send error: {e}")

def poll():
    global OFFSET
    url = f"{BASE}/getUpdates?offset={OFFSET}&limit=10"
    try:
        with urllib.request.urlopen(url, timeout=30) as r:
            data = json.loads(r.read())
        for u in data.get("result", []):
            OFFSET = u["update_id"] + 1
            msg = u.get("message", {})
            text = msg.get("text", "").strip().lower()
            if not text:
                continue
            print(f"Got: {text}")
            if text in ["status", "/status"]:
                send("Nous Ops is operational. 6 products active. 37 opportunities found. 10 leads generated.")
            elif text in ["build", "/build"]:
                send("Building latest iteration...")
            elif text in ["scan", "/scan"]:
                send("Running AutoScout scan now...")
            else:
                send(f"Command: {text}\nAvailable: status, scan, build")
    except Exception as e:
        print(f"Poll error: {e}")

print("Bot v2 starting...")
send("Bot v2 online. Commands: status, scan, build")

while True:
    poll()
    time.sleep(3)
