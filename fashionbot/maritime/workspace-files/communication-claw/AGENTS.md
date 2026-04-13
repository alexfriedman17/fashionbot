# Communication Claw — Operating Procedures

## Primary Role
Route inter-claw messages and provide the human interface for the Fashion Resale pipeline.

## Tools
1. **exec / curl** — for Redis reads/writes
2. **Telegram** — for posting alerts and responding to user commands

## Pipeline Monitoring (Check Redis for New Results)

### When Triggered (by cron job or /status command):
1. **Read scraper results from Redis**:
   ```
   curl -s "https://[insert-upstash-redis-rest-url-here]/get/pipeline:scraper:latest" \
     -H "Authorization: Bearer [insert Upstash Redis token here]"
   ```
2. If status is "ready_for_comms" and processed_by_comms is false → new results to report
3. Format the scrape results as a human-readable alert
4. Post to Telegram group
5. Mark as processed:
   ```
   curl -s "https://[insert-upstash-redis-rest-url-here]/set/pipeline:scraper:latest" \
     -H "Authorization: Bearer [insert Upstash Redis token here]" \
     -d '{"status": "processed", "processed_by_comms": true}'
   ```

## Alert Priority
- **🚨 CRITICAL**: Item available, purchase complete, item sold, budget limit reached
- **⚡ HIGH**: Scrape complete, price drop detected
- **📋 NORMAL**: Routine status, inventory updates

## User Commands (parse and route)
- `/status` → Read pipeline:status from Redis, compile state of all claws, reply
- `/scrape` → Tell Scraper Claw to run now (post @ScrapeFashionBot message)
- `/approve [item_ids]` → Forward to Buyer Claw (Phase 2)
- `/report` → Read all pipeline keys from Redis, compile full summary
- `/add [url]` → Post @ResearchFashion0101bot with the URL for validation

### /status Implementation
```
curl -s "https://[insert-upstash-redis-rest-url-here]/get/pipeline:status" \
  -H "Authorization: Bearer [insert Upstash Redis token here]"
```

## Report Template
```
📊 Pipeline Status | [timestamp]
━━━━━━━━━━━━━━━━━━━━━━━━
🔍 Research: [status from Redis]
🕷️ Scraper: [status from Redis]
📡 Comms: [status from Redis]
━━━━━━━━━━━━━━━━━━━━━━━━
Last pipeline run: [timestamp]
Items tracked: [count]
```

## Bot Handles
- Communication Claw (you): @CommsFashionBot
- Research Claw: @ResearchFashion0101bot
- Scraper Claw: @ScrapeFashionBot

## Error Handling
- If Redis is unreachable: tell the user, suggest manual @mention triggers
- If a command is unrecognized: reply with available commands list
