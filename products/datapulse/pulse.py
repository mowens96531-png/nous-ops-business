#!/usr/bin/env python3
"""DataPulse v1 - Market Intelligence Feed
Aggregates signals from multiple sources into actionable intelligence reports.
"""

import json, urllib.request, sqlite3
from datetime import datetime, timedelta
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"
DATA_DIR.mkdir(exist_ok=True)
DB_PATH = DATA_DIR / "signals.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS signals (
            id INTEGER PRIMARY KEY,
            source TEXT,
            category TEXT,
            headline TEXT,
            summary TEXT,
            url TEXT,
            sentiment REAL,
            impact_score REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    return conn

def fetch_tech_news():
    """Fetch tech news from multiple sources."""
    signals = []
    
    # HN top stories
    try:
        req = urllib.request.Request(
            "https://hacker-news.firebaseio.com/v0/topstories.json",
            headers={'User-Agent': 'DataPulse/1.0'}
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            story_ids = json.loads(resp.read())[:15]
        
        for sid in story_ids:
            try:
                req = urllib.request.Request(
                    f"https://hacker-news.firebaseio.com/v0/item/{sid}.json",
                    headers={'User-Agent': 'DataPulse/1.0'}
                )
                with urllib.request.urlopen(req, timeout=10) as resp:
                    story = json.loads(resp.read())
                
                if not story or story.get('type') != 'story':
                    continue
                
                score = story.get('score', 0)
                comments = story.get('descendants', 0)
                impact = min((score + comments * 2) / 100, 10)
                
                signals.append({
                    'source': 'hn',
                    'category': 'tech',
                    'headline': story.get('title', ''),
                    'summary': f"Score: {score}, Comments: {comments}",
                    'url': story.get('url') or f"https://news.ycombinator.com/item?id={sid}",
                    'sentiment': 0.5,
                    'impact_score': impact
                })
            except:
                continue
    except Exception as e:
        print(f"HN error: {e}")
    
    return signals

def fetch_github_trends():
    """Fetch trending repositories."""
    signals = []
    
    try:
        date_str = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        url = f"https://api.github.com/search/repositories?q=created:>{date_str}&sort=stars&order=desc&per_page=10"
        req = urllib.request.Request(url, headers={'Accept': 'application/vnd.github.v3+json'})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read())
        
        for repo in data.get('items', []):
            stars = repo.get('stargazers_count', 0)
            impact = min(stars / 500, 10)
            
            signals.append({
                'source': 'github',
                'category': 'oss',
                'headline': f"{repo.get('full_name', 'unknown')} ({repo.get('language', 'N/A')})",
                'summary': (repo.get('description') or 'No description')[:200],
                'url': repo.get('html_url', ''),
                'sentiment': 0.7,
                'impact_score': impact
            })
    except Exception as e:
        print(f"GitHub error: {e}")
    
    return signals

def save_signals(signals):
    """Save signals to database."""
    conn = init_db()
    cursor = conn.cursor()
    
    saved = 0
    for sig in signals:
        try:
            cursor.execute("""
                INSERT INTO signals (source, category, headline, summary, url, sentiment, impact_score)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (sig['source'], sig['category'], sig['headline'], sig['summary'],
                  sig['url'], sig['sentiment'], sig['impact_score']))
            saved += 1
        except:
            pass
    
    conn.commit()
    conn.close()
    return saved

def generate_digest():
    """Generate a daily intelligence digest."""
    conn = init_db()
    cursor = conn.cursor()
    
    # Get top signals from last 24 hours
    yesterday = (datetime.now() - timedelta(days=1)).isoformat()
    cursor.execute("""
        SELECT source, category, headline, summary, url, impact_score
        FROM signals
        WHERE created_at > ?
        ORDER BY impact_score DESC
        LIMIT 20
    """, (yesterday,))
    
    signals = cursor.fetchall()
    conn.close()
    
    report = f"""# DataPulse Intelligence Digest
**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}

## Executive Summary
- Total signals: {len(signals)}
- Top sources: HN, GitHub
- High impact (8+): {len([s for s in signals if s[5] >= 8])}

## Top Signals

"""
    
    for i, (source, cat, headline, summary, url, impact) in enumerate(signals[:10], 1):
        report += f"""### {i}. {headline}
- **Source:** {source} | **Category:** {cat} | **Impact:** {impact:.1f}/10
- **Summary:** {summary}
- **Link:** {url}

"""
    
    # Categorize
    categories = {}
    for sig in signals:
        cat = sig[1]
        categories[cat] = categories.get(cat, 0) + 1
    
    report += "## Category Breakdown\n"
    for cat, count in sorted(categories.items(), key=lambda x: -x[1]):
        report += f"- {cat}: {count} signals\n"
    
    report += f"""
## Insights
- Most active source: {max(set([s[0] for s in signals]), key=lambda x: sum(1 for s in signals if s[0] == x)) if signals else 'N/A'}
- Average impact: {sum(s[5] for s in signals) / len(signals) if signals else 0:.1f}
- Recommendations: Focus on high-impact OSS projects and trending discussions

---
*DataPulse by Nous Ops — Autonomous Intelligence*
"""
    
    return report

def run_pulse():
    """Run full pulse cycle."""
    print(f"[{datetime.now()}] DataPulse starting...")
    
    all_signals = []
    all_signals.extend(fetch_tech_news())
    all_signals.extend(fetch_github_trends())
    
    saved = save_signals(all_signals)
    print(f"Saved {saved} signals")
    
    digest = generate_digest()
    digest_path = DATA_DIR / f"digest_{datetime.now().strftime('%Y%m%d_%H%M')}.md"
    digest_path.write_text(digest)
    print(f"Digest saved: {digest_path}")
    
    return digest_path

if __name__ == '__main__':
    report = run_pulse()
    print(f"Pulse complete: {report}")
