# Nous Ops — Company Overview

**Founded:** 2026-05-01
**Type:** Autonomous AI Company
**Model:** Multi-agent operations, 24/7 execution
**Status:** Active development, 5 products shipping

## Products

### 1. AutoScout (Active)
- **What:** Autonomous business opportunity scanner
- **Sources:** GitHub trending, Hacker News, patent databases
- **Output:** Ranked opportunity briefs with build recommendations
- **Schedule:** Hourly cron
- **Status:** 37 opportunities found, database active

### 2. AgentDeploy (Active)
- **What:** One-click agent infrastructure deployment
- **Templates:** Basic agent, multi-agent system
- **Stack:** FastAPI, Docker, Redis
- **Status:** 2 templates ready, on-demand deployment

### 3. DataPulse (Active)
- **What:** Market intelligence feed
- **Sources:** HN, GitHub, tech news
- **Output:** Daily digest with impact scoring
- **Schedule:** Daily cron at 9 AM
- **Status:** 16 signals captured

### 4. ContentForge (Active)
- **What:** Autonomous content generation
- **Output:** Social media posts, marketing copy
- **Schedule:** Daily batch generation
- **Status:** Templates ready, 2 posts generated

### 5. LeadGen (Active)
- **What:** Autonomous lead generation
- **Sources:** HN hiring, GitHub orgs
- **Output:** Scored leads with company info
- **Schedule:** Daily cron at 10 AM
- **Status:** 10 leads found, 6 ready for outreach

### 6. Outreach (Active)
- **What:** Personalized email generation
- **Input:** LeadGen database
- **Output:** Personalized outreach emails
- **Status:** 6 emails generated, ready to send

## Infrastructure

- **API Server:** FastAPI REST API (port 8000)
- **Database:** SQLite (products), JSON (configs)
- **Cron Jobs:** 3 scheduled (AutoScout hourly, DataPulse daily, LeadGen daily)
- **Telegram Bot:** Running, responds to commands
- **GitHub:** mowens96531-png/nous-ops-business
- **Website:** Static HTML landing page
- **Dashboard:** Admin overview page

## Agent Skills
- **Total:** 206 skills converted from agency-agents repo
- **Categories:** Engineering, marketing, sales, finance, design, product, operations
- **Format:** Hermes SKILL.md compatible

## Revenue Model
- **DataPulse:** $49-199/month
- **AgentDeploy:** $29-99 one-time
- **AutoScout:** $19-79/report
- **Consulting:** $500-5000

## Metrics
- Products: 6
- Agent skills: 206
- Opportunities found: 37
- Intelligence signals: 16
- Leads generated: 10
- Outreach emails: 6
- Commits: 8

## Next Milestones
1. Stripe payment integration
2. User authentication system
3. Product API monetization
4. Automated X/Twitter posting
5. Customer onboarding flow
