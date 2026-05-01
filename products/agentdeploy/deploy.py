#!/usr/bin/env python3
"""AgentDeploy v1 - One-click agent infrastructure deployment.
Deploys complete agent stacks to cloud providers.
"""

import json, os, sys
from pathlib import Path
from datetime import datetime

TEMPLATES = {
    "basic_agent": {
        "name": "Basic AI Agent",
        "description": "Simple agent with API + frontend",
        "stack": ["fastapi", "sqlite", "docker"],
        "files": {
            "Dockerfile": """FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
""",
            "requirements.txt": """fastapi==0.109.0
uvicorn==0.27.0
pydantic==2.5.0
""",
            "main.py": """from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="AI Agent API")

class Query(BaseModel):
    text: str

@app.post("/ask")
async def ask(query: Query):
    return {"response": f"Received: {query.text}"}

@app.get("/health")
async def health():
    return {"status": "ok"}
"""
        }
    },
    "multi_agent": {
        "name": "Multi-Agent System",
        "description": "Orchestrated multi-agent company",
        "stack": ["fastapi", "redis", "docker-compose"],
        "files": {
            "docker-compose.yml": """version: '3.8'
services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - REDIS_URL=redis://redis:6379
    depends_on:
      - redis
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
""",
            "Dockerfile": """FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0"]
""",
            "requirements.txt": """fastapi==0.109.0
uvicorn==0.27.0
redis==5.0.0
pydantic==2.5.0
""",
            "main.py": """from fastapi import FastAPI
import redis
import os

app = FastAPI(title="Multi-Agent System")
r = redis.Redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379"))

@app.get("/")
async def root():
    return {"agents": ["agent_1", "agent_2", "agent_3"], "status": "running"}

@app.get("/health")
async def health():
    try:
        r.ping()
        return {"status": "ok", "redis": "connected"}
    except:
        return {"status": "degraded", "redis": "disconnected"}
"""
        }
    }
}

def deploy_template(template_name, output_dir):
    """Generate deployment files for a template."""
    if template_name not in TEMPLATES:
        print(f"Unknown template: {template_name}")
        print(f"Available: {', '.join(TEMPLATES.keys())}")
        return None
    
    template = TEMPLATES[template_name]
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    
    for filename, content in template["files"].items():
        (out / filename).write_text(content)
        print(f"Created: {out / filename}")
    
    # Create deployment manifest
    manifest = {
        "template": template_name,
        "name": template["name"],
        "created_at": datetime.now().isoformat(),
        "stack": template["stack"],
        "files": list(template["files"].keys())
    }
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2))
    
    print(f"\nDeployment ready: {out}")
    print(f"Stack: {', '.join(template['stack'])}")
    print(f"\nTo deploy locally:")
    print(f"  cd {out}")
    if "docker-compose" in template["stack"]:
        print("  docker-compose up -d")
    else:
        print("  docker build -t agent . && docker run -p 8000:8000 agent")
    
    return out

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 deploy.py <template> <output_dir>")
        print(f"Templates: {', '.join(TEMPLATES.keys())}")
        sys.exit(1)
    
    deploy_template(sys.argv[1], sys.argv[2])
