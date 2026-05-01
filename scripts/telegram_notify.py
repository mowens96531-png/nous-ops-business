#!/usr/bin/env python3
"""Send notifications to Mike via Telegram."""
import sys, urllib.request, urllib.parse, json

TOKEN = "8681348118:AAF3cz-lvP17w6s4CMRughPOagdMuMH27Ug"
CHAT = "8486989098"

def send_message(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = urllib.parse.urlencode({"chat_id": CHAT, "text": text}).encode()
    req = urllib.request.Request(url, data=data, method="POST")
    req.add_header("Content-Type", "application/x-www-form-urlencoded")
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read())
    except Exception as e:
        print(f"Telegram error: {e}")
        return None

if __name__ == '__main__':
    if len(sys.argv) > 1:
        send_message(sys.argv[1])
    else:
        print("Usage: python3 telegram_notify.py 'message'")
