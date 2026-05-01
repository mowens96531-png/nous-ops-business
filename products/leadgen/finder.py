#!/usr/bin/env python3
"""LeadGen v1 - Autonomous lead generation for Nous Ops.
Finds potential customers based on signals and intent data.
"""

import json, urllib.request, sqlite3, re
from datetime import datetime
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"
DATA_DIR.mkdir(exist_ok=True)
DB_PATH = DATA_DIR / "leads.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY,
            source TEXT,
            company TEXT,
            contact TEXT,
            email TEXT,
            signal TEXT,
            score REAL,
            status TEXT DEFAULT 'new',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    return conn

def score_lead(company, signal, engagement=None):
    """Score a lead based on signals."""
    score = 30  # Base
    
    # Signal quality
    high_intent = ['looking for', 'need', 'want', 'hiring', 'build', 'automate',
                   'agent', 'ai', 'automation', 'infrastructure']
    text = (company + ' ' + signal).lower()
    for kw in high_intent:
        if kw in text: score += 10
    
    # Engagement
    if engagement:
        if engagement > 100: score += 15
        elif engagement > 50: score += 10
        elif engagement > 20: score += 5
    
    return min(score, 100)

def fetch_hn_hiring():
    """Fetch 'Who is hiring' posts from HN."""
    leads = []
    try:
        # Search for hiring posts
        req = urllib.request.Request(
            "https://hn.algolia.com/api/v1/search?query=hiring%20ai%20engineer%20OR%20hiring%20ml%20engineer&tags=story&numericFilters=created_at_i>1714521600",
            headers={'User-Agent': 'LeadGen/1.0'}
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read())
        
        for hit in data.get('hits', [])[:10]:
            title = hit.get('title', '')
            company = title.split(']')[0].replace('[', '') if '[' in title else 'Unknown'
            
            score = score_lead(company, title, hit.get('points', 0))
            leads.append({
                'source': 'hn_hiring',
                'company': company,
                'contact': '',
                'email': '',
                'signal': title,
                'score': score
            })
    except Exception as e:
        print(f"HN hiring error: {e}")
    
    return leads

def fetch_github_orgs():
    """Find orgs that recently starred agent repos."""
    leads = []
    try:
        # Search for companies with agent-related repos
        req = urllib.request.Request(
            "https://api.github.com/search/repositories?q=agent+automation+company&sort=updated&order=desc&per_page=10",
            headers={'Accept': 'application/vnd.github.v3+json'}
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read())
        
        for repo in data.get('items', []):
            owner = repo.get('owner', {})
            company = owner.get('login', '')
            if not company:
                continue
            
            score = score_lead(company, repo.get('description', ''), repo.get('stargazers_count', 0))
            leads.append({
                'source': 'github',
                'company': company,
                'contact': '',
                'email': '',
                'signal': repo.get('description', '')[:200],
                'score': score
            })
    except Exception as e:
        print(f"GitHub error: {e}")
    
    return leads

def save_leads(leads):
    """Save leads to database."""
    conn = init_db()
    cursor = conn.cursor()
    
    saved = 0
    for lead in leads:
        try:
            cursor.execute("""
                INSERT OR IGNORE INTO leads (source, company, contact, email, signal, score)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (lead['source'], lead['company'], lead['contact'],
                  lead['email'], lead['signal'], lead['score']))
            saved += 1
        except:
            pass
    
    conn.commit()
    conn.close()
    return saved

def generate_outreach_list():
    """Generate list of leads ready for outreach."""
    conn = init_db()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM leads WHERE score >= 60 AND status = 'new' ORDER BY score DESC")
    leads = cursor.fetchall()
    conn.close()
    
    return [dict(l) for l in leads]

def run_scan():
    """Run full lead generation cycle."""
    print(f"[{datetime.now()}] LeadGen starting...")
    
    all_leads = []
    all_leads.extend(fetch_hn_hiring())
    all_leads.extend(fetch_github_orgs())
    
    saved = save_leads(all_leads)
    print(f"Saved {saved} leads")
    
    # Generate outreach list
    outreach = generate_outreach_list()
    print(f"Leads ready for outreach: {len(outreach)}")
    
    # Save report
    report = f"""# LeadGen Report — {datetime.now().strftime('%Y-%m-%d %H:%M')}

## Summary
- New leads found: {saved}
- Total in database: {saved + len(outreach)}
- Ready for outreach (60+ score): {len(outreach)}

## Top Leads
"""
    for i, lead in enumerate(outreach[:10], 1):
        report += f"""{i}. **{lead['company']}** ({lead['source']}) — Score: {lead['score']}
   Signal: {lead['signal'][:100]}

"""
    
    report_path = DATA_DIR / f"report_{datetime.now().strftime('%Y%m%d_%H%M')}.md"
    report_path.write_text(report)
    print(f"Report saved: {report_path}")
    
    return report_path

if __name__ == '__main__':
    run_scan()
