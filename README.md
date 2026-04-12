# Fashion Resale Claws — Autonomous Fashion Resale Pipeline

An autonomous multi-agent system that monitors fashion item availability, validates listings, and alerts the team when items become purchasable. Built at a hackathon using Maritime/OpenClaw AI agents, Telegram, Upstash Redis, and a Python CLI scraper.

## Architecture

```
USER (Telegram)
  │
  ▼
┌──────────────┐     Redis: pipeline:research:latest     ┌──────────────┐
│ RESEARCH     │ ──────────────────────────────────────►  │ SCRAPER      │
│ CLAW         │  Validates items, rejects eBay,          │ CLAW         │
│ (Maritime)   │  finds alternatives                      │ (Maritime)   │
└──────────────┘                                          └──────┬───────┘
                                                                 │
                    Redis: pipeline:scraper:latest                │
┌──────────────┐  ◄──────────────────────────────────────────────┘
│ COMMS CLAW   │  Compiles alerts, posts to Telegram,
│ (Maritime)   │  handles /status, /scrape, /report
└──────────────┘
       │
       ▼
  TELEGRAM GROUP (human-visible + inter-agent)
```

**Two scraping approaches run in parallel:**

1. **Maritime Agents** — AI agents on Maritime.sh with `web_fetch` + ScraperAPI proxy. They read/write Redis for autonomous handoffs and post to Telegram for visibility.
2. **Python CLI** (`fashionbot/`) — Playwright-based local scraper for reliable, headless browser checks with site-specific classifiers.

## Quick Start

### Python CLI (Local Scraping)

```bash
pip install -e .[dev]
python -m playwright install chromium
python -m fashionbot check          # check all items in watchlist.json
python -m fashionbot check --recap  # full status report
```

### Maritime Agents (Telegram)

Agents are hosted on [Maritime.sh](https://maritime.sh). Each agent has its own Telegram bot:

| Agent | Telegram Bot | Role |
|-------|-------------|------|
| research-claw | @ResearchFashion0101bot | Validates items, rejects eBay, finds alternatives |
| scraper-claw | @ScrapeFashionBot | Checks availability via web_fetch + ScraperAPI |
| communication-claw | @CommsFashionBot | Routes messages, compiles reports, handles commands |

**Telegram commands:** `/status`, `/scrape`, `/report`, `/add [url]`, `/approve [ids]`

## Project Structure

```
fashionbot/
├── README.md                          ← You are here
├── watchlist.json                     ← Canonical item list (source of truth)
├── watchlist.md                       ← Generated human-readable mirror
├── pyproject.toml                     ← Python package config
│
├── fashionbot/                        ← Python CLI scraper
│   ├── checker.py                     ← Playwright browser orchestration
│   ├── classifiers.py                 ← Availability signal classification
│   ├── cli.py                         ← Command-line interface
│   ├── models.py                      ← Data models
│   ├── storage.py                     ← JSON load/save
│   ├── dashboard.py                   ← HTML dashboard generation
│   ├── markdown.py                    ← Markdown report generation
│   ├── reporting.py                   ← Status change reporting
│   └── sites/                         ← Site-specific scrapers
│       ├── topologie.py               ← Shopify-based (uses .json endpoint)
│       ├── coach.py                   ← Coach.com parser
│       ├── lego.py                    ← LEGO.com parser
│       └── generic.py                 ← Fallback HTML signal parser
│
├── maritime/                          ← OpenClaw agent configuration
│   ├── DEMO-WALKTHROUGH.md            ← Step-by-step demo with copy-paste prompts
│   ├── workspace-files/               ← Agent personality + procedures
│   │   ├── research-claw/
│   │   │   ├── SOUL.md                ← Identity + personality
│   │   │   └── AGENTS.md              ← Operating procedures + Redis handoff
│   │   ├── scraper-claw/
│   │   │   ├── SOUL.md
│   │   │   └── AGENTS.md              ← Scraping procedures + Shopify .json trick
│   │   └── communication-claw/
│   │       ├── SOUL.md
│   │       └── AGENTS.md              ← Message routing + Redis polling
│   └── diagrams/
│       ├── architecture-figma.png     ← Visual architecture diagram
│       └── system-architecture.mermaid
│
├── blockdiagrams/                     ← Pipeline flow diagrams (Mermaid)
├── docs/                              ← Technical documentation
│   ├── PRODUCT_PRD.md
│   ├── TECHNICAL_PRD.md
│   ├── SCRAPING_APPROACH.md
│   ├── SITE_CHECKING_STRATEGY.md
│   └── BROWSER_BACKENDS.md
│
├── tests/                             ← Test suite
└── .github/workflows/                 ← CI: auto-check every 30 min
```

## How It Works

### Pipeline Flow

1. **User submits items** → @mention Research Claw in Telegram with URLs + preferences
2. **Research Claw validates** → rejects eBay, checks platforms, extracts details, writes to Redis
3. **Scraper Claw picks up** → reads Redis (cron every 2 min), checks each URL via ScraperAPI or Shopify JSON, writes results
4. **Comms Claw reports** → reads Redis, formats alert (🚨 available / ❌ sold out / ⚠️ unknown), posts to Telegram
5. **Human approves** → `/approve [ids]` triggers Buyer Claw (Phase 2)

### Redis Pipeline (Shared Brain)

| Key | Written By | Read By |
|-----|-----------|---------|
| `pipeline:research:latest` | Research Claw | Scraper Claw |
| `pipeline:scraper:latest` | Scraper Claw | Comms Claw |
| `pipeline:status` | All claws | All claws |

### Current Watchlist

| Item | Status | Price Target |
|------|--------|-------------|
| Topologie Bomber Strap | ❌ Sold Out | $75 |
| Topologie Scrunchie Pocket Wrist | ❌ Sold Out | $82 |
| Topologie Bungee Wrist Strap | ✅ Available (Mint) | $45 |
| Coach Coachtopia Small Slouchy | ⚠️ Manual Check | — |
| Coach Coachtopia Alter/Ego | ⚠️ Manual Check | — |
| LEGO Brick Clog | ❌ Sold Out | — |

## Infrastructure

| Service | Purpose | Cost |
|---------|---------|------|
| Maritime.sh | Agent hosting (3 agents) | $3/mo |
| Telegram | User interface + inter-agent visibility | Free |
| Upstash Redis | Shared pipeline state | Free tier |
| ScraperAPI | Proxy for web fetching | Free tier (1K calls/mo) |
| GitHub Actions | Auto-check every 30 min | Free |

## Team

- **Quilee** — Pipeline orchestration, Maritime agent config, Telegram architecture
- **Alex** — Python CLI scraper, site-specific parsers, Playwright automation
- **Ze'ev** — Infrastructure, Redis setup, integration testing

## Roadmap

- [x] Research Claw: validates items, outputs structured JSON
- [x] Scraper Claw: checks availability via web_fetch + ScraperAPI
- [x] Communication Claw: routes messages, /status command
- [x] Python CLI: Playwright-based local scraper with site parsers
- [x] Redis pipeline: shared state between agents
- [x] Telegram: all 3 bots responding in group
- [ ] Cron jobs: auto-poll Redis every 2 minutes
- [ ] Full autonomous pipeline: end-to-end without human triggers
- [ ] Buyer Claw: auto-purchase approved items (Phase 2)
- [ ] Seller Claw: auto-list on Poshmark (Phase 2)

## License

MIT
