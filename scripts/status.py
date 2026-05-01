#!/usr/bin/env python3
"""Quick status report for Nous Ops."""
import subprocess, json
from datetime import datetime

def run(cmd):
    try:
        return subprocess.check_output(cmd, shell=True, text=True, timeout=10).strip()
    except:
        return "N/A"

cron_jobs = run("hermes cron list 2>/dev/null || echo 'No cron jobs'")
repo_status = run("cd ~/workspace/nous-ops-business && git log --oneline -3 2>/dev/null || echo 'No git'")
disk = run("df -h /Users/founderagent | tail -1 | awk '{print $4}'")

print(f"""Nous Ops Status — {datetime.now().strftime('%H:%M')}

Disk: {disk} free
Commits: 
{repo_status}

Cron Jobs:
{cron_jobs}
""")
