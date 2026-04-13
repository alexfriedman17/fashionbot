# Demo Walkthrough — Exact Prompts to Copy-Paste
**Fashion Resale Claws | April 12, 2026**

---

## Pre-Demo: What's Already Set Up
- ✅ Redis has Alex's 6 validated items loaded at `pipeline:research:latest` with status `ready_for_scraper`
- ✅ All 3 agents have Redis env vars (UPSTASH_REDIS_REST_URL + UPSTASH_REDIS_REST_TOKEN)
- ✅ All 3 agents know about Redis pipeline (taught via dashboard chat)
- ✅ Scraper has ScraperAPI key for web fetching

---

## DEMO STEP 1: Show Research Claw Validating (Telegram)

In the Telegram group chat, send:

```
@ResearchFashion0101bot Please validate these 3 items:

1. Topologie Bomber Strap - https://topologie.com/products/bomber-strap - Any color - Max $75
2. Coach Coachtopia Small Slouchy Shoulder Bag - https://www.coach.com/products/coachtopia/small-slouchy-shoulder-bag-in-upcrafted-patchwork/CFF99-Z6Q.html
3. LEGO Brick Clog - https://www.lego.com/en-us/product/brick-clog-5010203 - Size M8/M9/M10

Constraints: No eBay. Write results to Redis pipeline when done.
```

**What happens:** Research Claw validates each URL, outputs structured JSON, and (if working) writes to Redis.

**If Research Claw doesn't write to Redis** (rate limit, etc.), that's fine — I already loaded the data into Redis for you.

---

## DEMO STEP 2: Trigger Scraper via Telegram (Manual Trigger)

Since cron jobs might not be set up yet, manually trigger the Scraper. In Telegram group:

```
@ScrapeFashionBot Check Redis for new work. Read the pipeline:research:latest key from Upstash Redis. You should find 6 validated items. Scrape each URL for availability. For Shopify stores (topologie.com), fetch the .json endpoint (e.g. https://topologie.com/products/bomber-strap.json) and check variants[].available. Write your results to pipeline:scraper:latest in Redis when done.
```

**What happens:** Scraper reads from Redis, scrapes each URL, writes results back.

**If Scraper can't read Redis from Telegram** (the agent may not execute curl from a Telegram message), do this instead via the **OpenClaw Dashboard**:

Go to Maritime → scraper-claw → OpenClaw Dashboard → Chat. Paste:

```
Check Redis for new work now. Read the key pipeline:research:latest from Upstash Redis using your configured credentials. You should find 6 validated items with status "ready_for_scraper". For each item:

1. If it's a Shopify store (topologie.com), fetch URL.json first (e.g. https://topologie.com/products/bomber-strap.json) and check product.variants[].available
2. For coach.com, fetch the regular URL and look for "Add to Bag" or "Sold Out" in the HTML
3. For lego.com, fetch the URL and look for "Add to Bag" or "Sold Out"

After checking all items, write your results to Redis key pipeline:scraper:latest with status "ready_for_comms". Also post your results to the Telegram group.
```

---

## DEMO STEP 3: Trigger Comms Alert (Manual Trigger)

After Scraper finishes, trigger Comms. In Telegram group:

```
@CommsFashionBot Check Redis for new scraper results. Read pipeline:scraper:latest. If there are results, compile a formatted alert report and post it here. Use 🚨 for available items, ❌ for sold out, ⚠️ for unknown.
```

**Or via OpenClaw Dashboard** (Maritime → communication-claw → Chat):

```
Check Redis now. Read the key pipeline:scraper:latest from Upstash Redis. If status is "ready_for_comms", format the scrape results as a nice alert report and post it to the Telegram group. Mark it as processed when done.
```

---

## DEMO STEP 4: Show Status Command

In Telegram group:

```
@CommsFashionBot /status
```

**Expected:** Comms Claw reads pipeline:status from Redis and reports the state of all claws.

**If /status doesn't read from Redis**, try:

```
@CommsFashionBot Read pipeline:status from Redis and tell me the current state of the pipeline. What is each claw doing?
```

---

## DEMO STEP 5: Show the Pipeline Visibility

Point out to judges/audience:
- "Look at the Telegram chat — you can see each agent working in sequence"
- "Research validated the items, Scraper checked availability, Comms compiled the report"
- "Redis is the shared brain — each agent reads and writes to it independently"
- "The human only needs to submit items and approve purchases"

---

## FALLBACK: If Redis Pipeline Doesn't Work End-to-End

If the agents can't reliably read/write Redis from Telegram, run the demo as a **manually-triggered pipeline** where you @mention each bot in sequence:

**Step 1 (Research):**
```
@ResearchFashion0101bot Validate these items:
1. Topologie Bomber Strap - https://topologie.com/products/bomber-strap - Max $75
2. Coach Slouchy Bag - https://www.coach.com/products/coachtopia/small-slouchy-shoulder-bag-in-upcrafted-patchwork/CFF99-Z6Q.html
3. LEGO Brick Clog - https://www.lego.com/en-us/product/brick-clog-5010203 - Size M8-M10
No eBay.
```

**Step 2 (Scraper) — after Research responds:**
```
@ScrapeFashionBot Please check availability for these validated items:
1. https://topologie.com/products/bomber-strap (Shopify - use .json endpoint)
2. https://www.coach.com/products/coachtopia/small-slouchy-shoulder-bag-in-upcrafted-patchwork/CFF99-Z6Q.html
3. https://www.lego.com/en-us/product/brick-clog-5010203
Report availability status and prices for each.
```

**Step 3 (Comms) — after Scraper responds:**
```
@CommsFashionBot Compile a report from the scraper results above. Format as availability alert with 🚨 ❌ ⚠️ indicators.
```

**Step 4 (Status):**
```
@CommsFashionBot /status
```

This still shows the multi-agent pipeline working, even if the Redis handoff isn't fully automated yet.

---

## KEY TALKING POINTS FOR JUDGES

1. **"This is an autonomous company — AI agents that research, monitor, and report on fashion items 24/7"**

2. **"Three specialized agents, each with their own role:"**
   - Research Claw: validates items, rejects bad links, finds alternatives
   - Scraper Claw: checks real availability using ScraperAPI, parses Shopify JSON
   - Communication Claw: routes messages, compiles alerts, responds to commands

3. **"Redis is the shared brain — agents read and write independently"**
   - Research writes validated items → Scraper picks them up
   - Scraper writes availability results → Comms picks them up
   - Each agent can be replaced, upgraded, or scaled independently

4. **"The human only decides two things: what to track and what to buy"**
   - Submit items → Research validates → Scraper monitors → Comms alerts
   - User says /approve → Buyer Claw purchases (Phase 2)

5. **"Total cost: $3/month for 3 agents + free API tiers"**
   - Maritime: $1/agent/month
   - ScraperAPI: free tier (1000 calls)
   - Upstash Redis: free tier
   - Telegram: free

6. **"Phase 2 adds auto-purchasing and auto-listing on Poshmark — full autonomous resale loop"**

---

## CRON JOBS (Set Up When Rate Limits Clear)

When you can access OpenClaw Dashboard again:

### Scraper Claw — OpenClaw Dashboard → Cron Jobs (left sidebar)
- **Name:** check-for-research-results
- **Schedule:** `*/2 * * * *` (every 2 minutes)
- **Message:** Check Redis for new research results. Read pipeline:research:latest from Upstash Redis. If status is "ready_for_scraper" and processed_by_scraper is false, scrape all items in the list. For Shopify stores use the .json endpoint. Write results to pipeline:scraper:latest and post to Telegram.

### Communication Claw — OpenClaw Dashboard → Cron Jobs
- **Name:** check-for-scraper-results
- **Schedule:** `*/2 * * * *` (every 2 minutes)
- **Message:** Check Redis for new scraper results. Read pipeline:scraper:latest from Upstash Redis. If status is "ready_for_comms" and processed_by_comms is false, compile an alert report and post it to Telegram. Mark as processed.

---

## AFTER THE DEMO

If you want to make it fully autonomous later:
1. Set up the cron jobs above
2. The pipeline becomes: Human submits items → everything else is automatic
3. Add Buyer Claw (Phase 2) that reads approved items from Redis
4. Add Seller Claw that auto-lists purchased items on Poshmark
