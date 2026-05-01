#!/usr/bin/env python3
"""Convert agency-agents markdown files to Hermes SKILL.md format."""

import os, re, yaml
from pathlib import Path

AGENCY_DIR = Path.home() / "workspace/github-repos/agency-agents"
SKILLS_DIR = Path.home() / ".hermes/skills/agency"

def parse_agency_md(filepath):
    """Parse agency-agents markdown into structured data."""
    content = filepath.read_text()
    
    # Extract frontmatter if present
    frontmatter = {}
    body = content
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            try:
                frontmatter = yaml.safe_load(parts[1])
                body = parts[2].strip()
            except:
                pass
    
    # Extract role/title
    title = frontmatter.get('name', '')
    if not title:
        # Try to extract from first heading
        match = re.search(r'^#\s+(.+)$', body, re.MULTILINE)
        if match:
            title = match.group(1).strip()
    
    # Extract description
    description = frontmatter.get('description', '')
    if not description:
        # First paragraph after title
        match = re.search(r'\n\n(.+?)\n\n', body)
        if match:
            description = match.group(1).strip()[:200]
    
    # Extract department from path
    dept = filepath.parent.name
    
    return {
        'title': title or filepath.stem.replace('-', ' ').title(),
        'description': description or f'{dept} agent skill',
        'department': dept,
        'body': body
    }

def convert_to_hermes_skill(data, output_path):
    """Convert parsed data to Hermes SKILL.md format."""
    skill_name = data['title'].lower().replace(' ', '-').replace('/', '-')
    
    skill_content = f"""---
name: {data['title']}
description: {data['description']}
category: agency-{data['department']}
---

# {data['title']}

**Department:** {data['department']}
**Source:** agency-agents repo

{data['body']}
"""
    
    output_path.write_text(skill_content)
    return skill_name

def main():
    SKILLS_DIR.mkdir(parents=True, exist_ok=True)
    
    md_files = list(AGENCY_DIR.rglob("*.md"))
    converted = 0
    
    for md_file in md_files:
        if '.git' in str(md_file) or md_file.name in ['README.md', 'CONTRIBUTING.md', 'CONTRIBUTING_zh-CN.md', 'LICENSE', 'SECURITY.md']:
            continue
        
        try:
            data = parse_agency_md(md_file)
            skill_name = data['title'].lower().replace(' ', '-').replace('/', '-')
            output_path = SKILLS_DIR / f"{skill_name}.md"
            convert_to_hermes_skill(data, output_path)
            converted += 1
        except Exception as e:
            print(f"Error converting {md_file}: {e}")
    
    print(f"Converted {converted} agency skills to Hermes format")
    print(f"Output: {SKILLS_DIR}")

if __name__ == '__main__':
    main()
