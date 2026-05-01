#!/usr/bin/env python3
"""ContentForge v1 - Autonomous content generation for Nous Ops marketing.
Generates social media posts, blog outlines, and email copy based on product updates.
"""

import json, random
from datetime import datetime
from pathlib import Path

TEMPLATES = {
    "product_launch": [
        "Shipped: {product_name} — {description}\n\nWhat it does:\n{features}\n\nBuilt autonomously. No human in the loop.\n\n{link}",
        "New from Nous Ops: {product_name}\n\n{description}\n\n{features}\n\n24/7 autonomous development. Try it: {link}",
    ],
    "milestone": [
        "Nous Ops milestone: {metric}\n\nWhat we're building:\n{description}\n\nAutonomous AI company, shipping daily.\n\n{link}",
        "{metric} and counting.\n\nNous Ops is an autonomous AI company that builds, tests, and ships products without human intervention.\n\nLatest: {description}\n\n{link}",
    ],
    "insight": [
        "Market insight from DataPulse:\n\n{insight}\n\nSource: {source}\n\nAutonomous intelligence, updated hourly.",
        "What we're tracking:\n\n{insight}\n\nSignal strength: {score}/10\n\nDataPulse by Nous Ops",
    ]
}

PRODUCTS = {
    "AutoScout": {
        "description": "Autonomous business opportunity scanner",
        "features": "- Scans GitHub trending hourly\n- Monitors Hacker News discussions\n- Scores opportunities by market potential\n- Generates build briefs automatically",
        "link": "github.com/mowens96531-png/nous-ops-business/tree/main/products/autoscout"
    },
    "AgentDeploy": {
        "description": "One-click agent infrastructure deployment",
        "features": "- Docker templates for single/multi-agent systems\n- FastAPI + Redis stacks\n- Production-ready configs\n- Deploy in 60 seconds",
        "link": "github.com/mowens96531-png/nous-ops-business/tree/main/products/agentdeploy"
    },
    "DataPulse": {
        "description": "Market intelligence feed",
        "features": "- Aggregates tech news signals\n- Scores by impact and sentiment\n- Daily digest generation\n- Multi-source coverage",
        "link": "github.com/mowens96531-png/nous-ops-business/tree/main/products/datapulse"
    }
}

def generate_post(post_type="product_launch", product=None, custom_data=None):
    """Generate a social media post."""
    if post_type not in TEMPLATES:
        return None
    
    template = random.choice(TEMPLATES[post_type])
    data = custom_data or {}
    
    if product and product in PRODUCTS:
        p = PRODUCTS[product]
        data.update({
            "product_name": product,
            "description": p["description"],
            "features": p["features"],
            "link": p["link"]
        })
    
    return template.format(**data)

def generate_daily_batch():
    """Generate a batch of posts for the day."""
    posts = []
    
    # One product highlight
    product = random.choice(list(PRODUCTS.keys()))
    posts.append(generate_post("product_launch", product=product))
    
    # One milestone/update
    posts.append(generate_post("milestone", custom_data={
        "metric": "3 products shipping",
        "description": "Autonomous development infrastructure for AI-native companies",
        "link": "github.com/mowens96531-png/nous-ops-business"
    }))
    
    return posts

def save_posts():
    """Save daily post batch."""
    posts = generate_daily_batch()
    output_dir = Path(__file__).parent / "output"
    output_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M')
    output_file = output_dir / f"posts_{timestamp}.txt"
    output_file.write_text("\n\n---\n\n".join(posts))
    
    print(f"Generated {len(posts)} posts")
    print(f"Saved: {output_file}")
    
    return output_file

if __name__ == '__main__':
    save_posts()
