#!/usr/bin/env python3
"""Nous Ops API Server
Exposes all products as REST API endpoints.
"""

import json, sqlite3, sys
from datetime import datetime
from pathlib import Path
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Nous Ops API", version="1.0.0")

BASE_DIR = Path(__file__).parent.parent

class QueryRequest(BaseModel):
    query: str
    limit: int = 10

@app.get("/")
async def root():
    return {
        "name": "Nous Ops",
        "version": "1.0.0",
        "products": ["autoscout", "datapulse", "agentdeploy"],
        "status": "operational"
    }

@app.get("/health")
async def health():
    return {"status": "ok", "timestamp": datetime.now().isoformat()}

@app.get("/opportunities")
async def get_opportunities(limit: int = 10, min_score: float = 0):
    """Get latest opportunities from AutoScout."""
    db_path = BASE_DIR / "products/autoscout/data/opportunities.db"
    if not db_path.exists():
        raise HTTPException(status_code=404, detail="No opportunities found")
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM opportunities WHERE score >= ? ORDER BY score DESC LIMIT ?",
        (min_score, limit)
    )
    rows = cursor.fetchall()
    conn.close()
    
    return {"opportunities": [dict(r) for r in rows], "count": len(rows)}

@app.get("/signals")
async def get_signals(limit: int = 10, category: str = None):
    """Get latest intelligence signals from DataPulse."""
    db_path = BASE_DIR / "products/datapulse/data/signals.db"
    if not db_path.exists():
        raise HTTPException(status_code=404, detail="No signals found")
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    if category:
        cursor.execute(
            "SELECT * FROM signals WHERE category = ? ORDER BY impact_score DESC LIMIT ?",
            (category, limit)
        )
    else:
        cursor.execute(
            "SELECT * FROM signals ORDER BY impact_score DESC LIMIT ?",
            (limit,)
        )
    
    rows = cursor.fetchall()
    conn.close()
    
    return {"signals": [dict(r) for r in rows], "count": len(rows)}

@app.get("/deploy/{template}")
async def deploy_template(template: str):
    """Get deployment template from AgentDeploy."""
    templates = {
        "basic_agent": BASE_DIR / "products/agentdeploy/templates/basic",
        "multi_agent": BASE_DIR / "products/agentdeploy/templates/multi"
    }
    
    if template not in templates:
        raise HTTPException(status_code=404, detail=f"Template '{template}' not found")
    
    return {"template": template, "status": "available", "deploy_url": f"/deploy/{template}/generate"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
