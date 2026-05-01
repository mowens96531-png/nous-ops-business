#!/usr/bin/env python3
"""AutoScout v1 - Autonomous Business Opportunity Scanner
Scans multiple sources for actionable business opportunities:
- Expired patents with commercial potential
- GitHub trending repos with market gaps
- Reddit/HN discussions with unsolved problems
- App Store gaps and niches

Outputs: Ranked opportunity briefs with build recommendations.
"""

import json, re, urllib.request, urllib.parse, sqlite3
from datetime import datetime, timedelta
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"
DATA_DIR.mkdir(exist_ok=True)

DB_PATH = DATA_DIR / "opportunities.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS opportunities (
            id INTEGER PRIMARY KEY,
            source TEXT,
            title TEXT,
            description TEXT,
            url TEXT,
            score REAL,
            category TEXT,
            tags TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'new'
        )
    """)
    conn.commit()
    return conn

def score_opportunity(title, description, source, engagement=None):
    """Score an opportunity based on multiple factors."""
    score = 50  # Base score
    
    # Engagement boost
    if engagement and isinstance(engagement, (int, float)):
        if engagement > 1000: score += 25
        elif engagement > 500: score += 15
        elif engagement > 100: score += 10
        elif engagement > 50: score += 5
    
    # Keyword scoring
    high_value_keywords = ['automation', 'ai', 'agent', 'saas', 'b2b', 'revenue', 
                          ' profitable', 'market', 'scale', 'infrastructure']
    med_value_keywords = ['tool', 'api', 'integration', 'workflow', 'analytics',
                         'monitoring', 'security', 'compliance']
    
    text = (title + ' ' + description).lower()
    for kw in high_value_keywords:
        if kw in text: score += 5
    for kw in med_value_keywords:
        if kw in text: score += 2
    
    # Source weighting
    source_weights = {'github_trending': 10, 'reddit': 8, 'hn': 8, 'patent': 5}
    score += source_weights.get(source, 0)
    
    return min(score, 100)

def fetch_github_trending():
    """Fetch trending repos from GitHub."""
    opportunities = []
    try:
        # Search for repos created in last 7 days with high stars
        date_str = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        url = f"https://api.github.com/search/repositories?q=created:>{date_str}&sort=stars&order=desc&per_page=20"
        req = urllib.request.Request(url, headers={'Accept': 'application/vnd.github.v3+json'})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read())
        
        for repo in data.get('items', []):
            score = score_opportunity(
                repo['name'], 
                repo.get('description', ''),
                'github_trending',
                repo.get('stargazers_count', 0)
            )
            opportunities.append({
                'source': 'github_trending',
                'title': f"{repo['full_name']} ({repo['language'] or 'unknown'})",
                'description': repo.get('description', 'No description')[:300],
                'url': repo['html_url'],
                'score': score,
                'category': 'open_source',
                'tags': json.dumps([repo.get('language', 'unknown'), 'github', 'trending'])
            })
    except Exception as e:
        print(f"GitHub fetch error: {e}")
    
    return opportunities

def fetch_hn_frontpage():
    """Fetch Hacker News frontpage."""
    opportunities = []
    try:
        # Get top stories
        req = urllib.request.Request(
            "https://hacker-news.firebaseio.com/v0/topstories.json",
            headers={'User-Agent': 'AutoScout/1.0'}
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            story_ids = json.loads(resp.read())[:20]
        
        for sid in story_ids:
            try:
                req = urllib.request.Request(
                    f"https://hacker-news.firebaseio.com/v0/item/{sid}.json",
                    headers={'User-Agent': 'AutoScout/1.0'}
                )
                with urllib.request.urlopen(req, timeout=10) as resp:
                    story = json.loads(resp.read())
                
                if not story or story.get('type') != 'story':
                    continue
                
                score = score_opportunity(
                    story.get('title', ''),
                    '',
                    'hn',
                    story.get('score', 0)
                )
                opportunities.append({
                    'source': 'hn',
                    'title': story.get('title', 'Untitled'),
                    'description': f"HN Score: {story.get('score', 0)}, Comments: {story.get('descendants', 0)}",
                    'url': story.get('url') or f"https://news.ycombinator.com/item?id={sid}",
                    'score': score,
                    'category': 'discussion',
                    'tags': json.dumps(['hackernews', 'discussion'])
                })
            except:
                continue
    except Exception as e:
        print(f"HN fetch error: {e}")
    
    return opportunities

def generate_opportunity_brief(opp):
    """Generate a build brief for a high-scoring opportunity."""
    if opp['score'] < 70:
        return None
    
    brief = f"""# Opportunity Brief: {opp['title']}

**Source:** {opp['source']}
**Score:** {opp['score']}/100
**URL:** {opp['url']}

## Description
{opp['description']}

## Why This Matters
This opportunity scored high due to:
- Strong engagement signals
- Market-relevant keywords
- Actionable build potential

## Suggested Actions
1. Research the market gap more deeply
2. Build a minimal version in 48 hours
3. Validate with 3 potential customers
4. If validated, scale aggressively

## Build Stack Recommendation
- Frontend: Next.js or vanilla HTML
- Backend: Python FastAPI or Node.js
- AI: Claude API or local models via Ollama
- Deployment: Vercel + Railway/Render
- Database: SQLite (start) → PostgreSQL (scale)

---
Generated by AutoScout v1 at {datetime.now().isoformat()}
"""
    return brief

def save_opportunities(opportunities):
    """Save opportunities to database."""
    conn = init_db()
    cursor = conn.cursor()
    
    saved = 0
    for opp in opportunities:
        try:
            cursor.execute("""
                INSERT INTO opportunities (source, title, description, url, score, category, tags)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (opp['source'], opp['title'], opp['description'], opp['url'],
                  opp['score'], opp['category'], opp['tags']))
            saved += 1
        except sqlite3.IntegrityError:
            pass  # Duplicate
    
    conn.commit()
    conn.close()
    return saved

def run_scan():
    """Run full scan cycle."""
    print(f"[{datetime.now()}] AutoScout scan starting...")
    
    all_opportunities = []
    all_opportunities.extend(fetch_github_trending())
    all_opportunities.extend(fetch_hn_frontpage())
    
    # Sort by score
    all_opportunities.sort(key=lambda x: x['score'], reverse=True)
    
    # Save to DB
    saved = save_opportunities(all_opportunities)
    print(f"Saved {saved} opportunities")
    
    # Generate briefs for top 5
    top_opps = all_opportunities[:5]
    briefs = []
    for opp in top_opps:
        brief = generate_opportunity_brief(opp)
        if brief:
            briefs.append(brief)
    
    # Write report
    report_path = DATA_DIR / f"report_{datetime.now().strftime('%Y%m%d_%H%M')}.md"
    report_content = f"""# AutoScout Report — {datetime.now().strftime('%Y-%m-%d %H:%M')}

## Summary
- Total opportunities found: {len(all_opportunities)}
- High-value opportunities (70+): {len([o for o in all_opportunities if o['score'] >= 70])}
- Sources scanned: GitHub Trending, Hacker News

## Top 10 Opportunities
"""
    for i, opp in enumerate(all_opportunities[:10], 1):
        report_content += f"{i}. **[{opp['score']}]** {opp['title']} — {opp['url']}\n"
    
    if briefs:
        report_content += "\n## Detailed Briefs\n\n"
        for brief in briefs:
            report_content += brief + "\n\n---\n\n"
    
    report_path.write_text(report_content)
    print(f"Report saved: {report_path}")
    
    return report_path

if __name__ == '__main__':
    report = run_scan()
    print(f"Scan complete. Report: {report}")
