# Sprint Plan — FINAL PUSH
**April 12, 2026 | ~2 hours remaining**

---

## The Architecture That Actually Works

The Telegram @mention handoff is broken (bot-to-bot mentions don't trigger in OpenClaw).  
The `sessions_send` approach may or may not work depending on config.  
**Redis is the answer.** Here's how it works:

```
┌─────────────┐     WRITES TO REDIS      ┌─────────────┐     WRITES TO REDIS      ┌─────────────┐
│  RESEARCH   │ ──────────────────────►   │   SCRAPER   │ ──────────────────────►   │    COMMS    │
│    CLAW     │  pipeline:research:latest │    CLAW     │  pipeline:scraper:latest  │    CLAW     │
└──────┬──────┘                           └──────┬──────┘                           └──────┬──────┘
       │                                         │                                         │
       │  CRON: polls Redis                      │  CRON: polls Redis                      │
       │  every 60s for new                      │  every 60s for new                      │
       │  /add commands                          │  research results                       │
       ▼                                         ▼                                         ▼
   Posts summary                             Posts results                            Posts alerts
   to Telegram                               to Telegram                              to Telegram
```

**Each agent does TWO things:**
1. **Writes results to Redis** when it finishes its job
2. **Polls Redis on a cron schedule** to check if the previous agent left new work

**Redis is the shared workspace. Telegram is the display. Cron jobs are the trigger.**

---

## Redis Keys (Already Set Up)

| Key | Written By | Read By | Purpose |
|-----|-----------|---------|---------| 
| `pipeline:research:latest` | Research Claw | Scraper Claw | Validated item list JSON |
| `pipeline:scraper:latest` | Scraper Claw | Comms Claw | Scrape results JSON |
| `pipeline:status` | All claws | All claws | Current state of each claw |

---

## STEP-BY-STEP: Set Up Redis Communication

### Step 1: Add Redis Env Vars to Each Agent (5 min)

For ALL THREE agents, go to Maritime → click agent → Env tab. Add:

```
UPSTASH_REDIS_REST_URL=https://[insert-upstash-redis-rest-url-here]
UPSTASH_REDIS_REST_TOKEN=[insert Upstash Redis token here]
```

### Step 2: Teach Each Agent How to Use Redis (10 min)

**In Research Claw's OpenClaw Dashboard → Chat, paste this:**

```
You now have access to Upstash Redis for pipeline communication. After you validate an item list, write the results to Redis so the Scraper Claw can pick them up.

To WRITE your validated list to Redis, use web_fetch or exec to run:

curl -s "https://[insert-upstash-redis-rest-url-here]/set/pipeline:research:latest" \
  -H "Authorization: Bearer [insert Upstash Redis token here]" \
  -d '{"item_list": [YOUR_VALIDATED_ITEMS], "status": "ready_for_scraper", "timestamp": "CURRENT_TIME", "processed_by_scraper": false}'

Also update the pipeline status:

curl -s "https://[insert-upstash-redis-rest-url-here]/set/pipeline:status" \
  -H "Authorization: Bearer [insert Upstash Redis token here]" \
  -d '{"research": "complete", "scraper": "pending", "comms": "idle"}'

After writing to Redis, post your summary to the Telegram group for human visibility.

This way the Scraper Claw will automatically pick up your results on its next poll cycle.
```

**In Scraper Claw's OpenClaw Dashboard → Chat, paste this:**

```
You now have access to Upstash Redis for pipeline communication. You have TWO jobs:

JOB 1 — CHECK FOR NEW WORK (do this when asked or on schedule):
Read the latest research results from Redis:

curl -s "https://[insert-upstash-redis-rest-url-here]/get/pipeline:research:latest" \
  -H "Authorization: Bearer [insert Upstash Redis token here]"

If the result has "status": "ready_for_scraper" and "processed_by_scraper": false, that means there's new work. Parse the item_list and scrape each URL.

JOB 2 — WRITE YOUR RESULTS:
After scraping all items, write results to Redis:

curl -s "https://[insert-upstash-redis-rest-url-here]/set/pipeline:scraper:latest" \
  -H "Authorization: Bearer [insert Upstash Redis token here]" \
  -d '{"scrape_results": [YOUR_RESULTS], "status": "ready_for_comms", "timestamp": "CURRENT_TIME", "processed_by_comms": false}'

Then mark the research results as processed:

curl -s "https://[insert-upstash-redis-rest-url-here]/set/pipeline:research:latest" \
  -H "Authorization: Bearer [insert Upstash Redis token here]" \
  -d '{"status": "processed", "processed_by_scraper": true}'

Also post your results to the Telegram group for human visibility.

IMPORTANT: For Shopify stores, ALWAYS fetch URL.json first (e.g. https://topologie.com/products/bomber-strap.json). This gives you variants[].available which is the most reliable stock check.
```

**In Communication Claw's OpenClaw Dashboard → Chat, paste this:**

```
You now have access to Upstash Redis for pipeline communication. You have TWO jobs:

JOB 1 — CHECK FOR SCRAPER RESULTS (do this when asked or on schedule):
Read the latest scrape results from Redis:

curl -s "https://[insert-upstash-redis-rest-url-here]/get/pipeline:scraper:latest" \
  -H "Authorization: Bearer [insert Upstash Redis token here]"

If the result has "status": "ready_for_comms" and "processed_by_comms": false, compile an alert and post it to the Telegram group.

JOB 2 — POST ALERTS:
Format the scrape results as a human-readable alert:
🚨 for available items, ❌ for sold out, ⚠️ for unknown.

Then mark the scraper results as processed:

curl -s "https://[insert-upstash-redis-rest-url-here]/set/pipeline:scraper:latest" \
  -H "Authorization: Bearer [insert Upstash Redis token here]" \
  -d '{"status": "processed", "processed_by_comms": true}'

JOB 3 — STATUS COMMAND:
When someone sends /status, read pipeline:status from Redis and report the current state of all claws.

curl -s "https://[insert-upstash-redis-rest-url-here]/get/pipeline:status" \
  -H "Authorization: Bearer [insert Upstash Redis token here]"
```

### Step 3: Set Up Cron Jobs (10 min)

This is what makes it AUTONOMOUS. Go to each agent's OpenClaw Dashboard → left sidebar → **Cron Jobs**.

**For Scraper Claw — Create a cron job:**
- Name: `check-for-research-results`
- Schedule: Every 2 minutes (or `*/2 * * * *`)
- Message: `Check Redis for new research results. Read pipeline:research:latest. If status is "ready_for_scraper" and processed_by_scraper is false, scrape all items in the list and write results back to Redis.`

**For Communication Claw — Create a cron job:**
- Name: `check-for-scraper-results`
- Schedule: Every 2 minutes (or `*/2 * * * *`)
- Message: `Check Redis for new scraper results. Read pipeline:scraper:latest. If status is "ready_for_comms" and processed_by_comms is false, compile an alert report and post it to Telegram.`

### Step 4: Test the Full Pipeline (10 min)

1. Send items to @ResearchFashion0101bot in Telegram
2. Research Claw validates → writes to Redis → posts summary to Telegram
3. Wait 2 minutes (or manually trigger Scraper: @ScrapeFashionBot check Redis for new work)
4. Scraper reads from Redis → scrapes URLs → writes results to Redis → posts to Telegram
5. Wait 2 minutes (or manually trigger Comms: @CommsFashionBot check Redis for new results)
6. Comms reads from Redis → posts formatted alert to Telegram

**If it works, the pipeline is autonomous.** Research finishes → Scraper auto-picks it up → Comms auto-reports.

---

## Demo Script (Final)

1. **"Watch us send 6 items to our AI research agent"** — @mention Research Claw with Alex's list
2. **"Research Claw validates everything and writes to our shared Redis pipeline"** — show Telegram + mention Redis
3. **"Within 2 minutes, Scraper Claw autonomously picks up the work"** — show it starting to scrape
4. **"Scraper checks each URL for real availability using ScraperAPI"** — show results with prices
5. **"Communication Claw automatically compiles and sends the alert"** — show the final report
6. **"The human only decides what to buy — everything else is autonomous"**

**Key talking points:**
- "Redis is our shared brain — agents read and write to it independently"
- "Cron jobs trigger each agent to check for new work every 2 minutes"
- "Telegram is the human-visible layer — you can watch the agents coordinate"
- "This is an autonomous company: research, monitoring, and reporting run 24/7"
- "Phase 2: auto-purchasing and auto-listing on Poshmark"

---

## Bot Handles
| Claw | Telegram | Maritime Agent ID |
|------|----------|-------------------|
| Communication | @CommsFashionBot | communication-claw |
| Research | @ResearchFashion0101bot | research-claw |
| Scraper | @ScrapeFashionBot | scraper-claw |
