# Fashion Resale Claws — Maritime Agent Configs

This directory contains everything needed to run the autonomous Maritime/OpenClaw agent pipeline. These are the actual workspace files deployed to [Maritime.sh](https://maritime.sh) agents that coordinate via Telegram and Upstash Redis.

## Structure

```
fashion-resale-claws/
├── workspace-files/           # Paste these into each agent's OpenClaw dashboard
│   ├── research-claw/         # Validates items, writes to Redis
│   │   ├── SOUL.md            # Agent personality
│   │   └── AGENTS.md          # Operating procedures + Redis handoff
│   ├── scraper-claw/          # Checks availability via web_fetch + ScraperAPI
│   │   ├── SOUL.md
│   │   └── AGENTS.md          # Shopify .json trick, platform parsers
│   └── communication-claw/    # Polls Redis, alerts team in Telegram
│       ├── SOUL.md
│       └── AGENTS.md          # /status, /scrape, /report commands
├── diagrams/                  # Architecture visuals (SVG, HTML, PNG, Mermaid source)
├── phase2-specs/              # Future claw designs (not yet built)
│   ├── buyer-claw.md          # Auto-purchase agent spec
│   └── seller-claw.md         # Poshmark listing agent spec
├── DEMO-WALKTHROUGH.md        # Exact copy-paste prompts for the hackathon demo
└── README.md                  # You are here
```

## Pipeline Flow

```
Research Claw ──writes──> Redis (pipeline:research:latest)
                              │
Scraper Claw  ──polls────────┘ ──writes──> Redis (pipeline:scraper:latest)
                                                │
Comms Claw    ──polls──────────────────────────┘ ──alerts──> Telegram group
```

Each agent runs on a cron job (every 60-120s) that polls Redis for new work. This sidesteps the OpenClaw limitation where bot-to-bot @mentions in Telegram don't trigger responses (bug #29626).

## Key Technical Details

- **ScraperAPI** proxies all web_fetch requests (free tier: 1000 calls/mo)
- **Shopify .json trick**: Append `.json` to any Shopify product URL for structured inventory data (`variants[].available`)
- **Upstash Redis** REST API for inter-agent state (free tier: 10k commands/day)
- **Telegram bot handles**: @ResearchFashion0101bot, @ScrapeFashionBot, @CommsFashionBot

## Setting Up From Scratch

1. Create 3 agents on [Maritime.sh](https://maritime.sh) ($1/agent/month)
2. For each agent, paste the corresponding `SOUL.md` and `AGENTS.md` into the workspace files panel
3. Create Telegram bots via @BotFather, set privacy to Disabled (`/setprivacy → Disable`)
4. Add all bots to the same Telegram group
5. Set environment variables on each agent: `SCRAPERAPI_KEY`, `UPSTASH_REDIS_URL`, `UPSTASH_REDIS_TOKEN`
6. Create cron jobs for Scraper and Comms to poll Redis every 60-120s
7. See `DEMO-WALKTHROUGH.md` for step-by-step testing prompts
