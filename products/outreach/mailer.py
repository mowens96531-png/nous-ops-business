#!/usr/bin/env python3
"""Outreach v1 - Autonomous email outreach system.
Generates personalized outreach emails for leads found by LeadGen.
"""

import sqlite3, json
from datetime import datetime
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"
DATA_DIR.mkdir(exist_ok=True)

LEADS_DB = Path.home() / "workspace/nous-ops-business/products/leadgen/data/leads.db"

def get_high_value_leads(limit=10):
    """Get leads ready for outreach."""
    if not LEADS_DB.exists():
        return []
    
    conn = sqlite3.connect(LEADS_DB)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM leads WHERE score >= 60 AND status = 'new' ORDER BY score DESC LIMIT ?",
        (limit,)
    )
    leads = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return leads

def generate_email(lead):
    """Generate personalized outreach email."""
    company = lead['company']
    signal = lead['signal']
    source = lead['source']
    
    # Determine angle based on signal
    if 'agent' in signal.lower() or 'ai' in signal.lower():
        angle = "agent infrastructure"
        product = "AgentDeploy"
    elif 'data' in signal.lower() or 'analytics' in signal.lower():
        angle = "market intelligence"
        product = "DataPulse"
    else:
        angle = "automation"
        product = "Nous Ops suite"
    
    subject = f"Quick question about {company}'s {angle}"
    
    body = f"""Hi there,

I noticed {company} is working on {signal[:80]}... 

We're building Nous Ops — an autonomous AI company that creates {angle} solutions. Our {product} helps teams like yours deploy faster and operate 24/7 without manual overhead.

Would you be open to a 10-minute chat about how we might help?

Best,
Nous Ops
https://github.com/mowens96531-png/nous-ops-business

P.S. Found you via {source} — love what you're building.
"""
    
    return {"subject": subject, "body": body, "lead_id": lead['id']}

def generate_outreach_batch():
    """Generate outreach emails for all high-value leads."""
    leads = get_high_value_leads()
    emails = []
    
    for lead in leads:
        email = generate_email(lead)
        emails.append(email)
    
    # Save batch
    timestamp = datetime.now().strftime('%Y%m%d_%H%M')
    output_file = DATA_DIR / f"outreach_{timestamp}.json"
    output_file.write_text(json.dumps(emails, indent=2))
    
    print(f"Generated {len(emails)} outreach emails")
    print(f"Saved: {output_file}")
    
    return emails

if __name__ == '__main__':
    generate_outreach_batch()
