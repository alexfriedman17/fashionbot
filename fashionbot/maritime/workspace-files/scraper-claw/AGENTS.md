# Scraper Claw — Operating Procedures

## Primary Role
Monitor item availability and price on target websites. Report findings with evidence.

## Tools
1. **web_fetch** — fetches page HTML. Use ScraperAPI proxy for blocked sites.
   Your ScraperAPI key is in TOOLS.md.
   Format: `http://api.scraperapi.com?api_key=[insert ScraperAPI key here]&url=TARGET_URL`
2. **exec / curl** — for Redis reads/writes and HTTP requests
3. **browser** — use if available (may not be on this machine)

## Workflow

### When Triggered (by cron job or human @mention):
1. **Read from Redis** to check for new work:
   ```
   curl -s "https://[insert-upstash-redis-rest-url-here]/get/pipeline:research:latest" \
     -H "Authorization: Bearer [insert Upstash Redis token here]"
   ```
2. If status is "ready_for_scraper" and processed_by_scraper is false → there's new work
3. Parse the item_list from the Redis value
4. For each item:
   a. **Shopify stores FIRST**: Fetch `URL.json` (e.g. `topologie.com/products/bomber-strap.json`)
      Parse `product.variants[].available` — this is the most reliable method
   b. **Non-Shopify**: Fetch regular URL via web_fetch, parse HTML for signals
   c. Extract: price, availability, variant/size info
5. **Write results to Redis**:
   ```
   curl -s "https://[insert-upstash-redis-rest-url-here]/set/pipeline:scraper:latest" \
     -H "Authorization: Bearer [insert Upstash Redis token here]" \
     -d '{"scrape_results": [RESULTS], "status": "ready_for_comms", "timestamp": "TIME", "processed_by_comms": false}'
   ```
6. Mark research as processed:
   ```
   curl -s "https://[insert-upstash-redis-rest-url-here]/set/pipeline:research:latest" \
     -H "Authorization: Bearer [insert Upstash Redis token here]" \
     -d '{"status": "processed", "processed_by_scraper": true}'
   ```
7. Post results to Telegram group for human visibility

## Platform-Specific Parsing

### Shopify Stores (Topologie, many DTC brands)
**ALWAYS try .json endpoint first:** `https://site.com/products/item-name.json`
Returns: `product.variants[].available` (true/false), prices, titles, images.
**NEVER report a Shopify product as UNKNOWN without trying .json first.**

### Coach / Large Retailers
HTML signals: "Add to Bag" → AVAILABLE, "Sold Out" → UNAVAILABLE
Check JSON-LD `<script type="application/ld+json">` for availability field.

### Nike.com
Use ScraperAPI with render=true: `api_key=[insert ScraperAPI key here]&url=URL&render=true`

### LEGO.com
HTML signals: "Add to Bag" → AVAILABLE, "Sold Out" → UNAVAILABLE

### Generic Fallback
AVAILABLE: "Add to Cart", "Add to Bag", "Buy Now", "In Stock"
UNAVAILABLE: "Sold Out", "Out of Stock", "Currently Unavailable", "No Longer Available", "Notify Me"
Also check JSON-LD for schema.org/InStock or schema.org/OutOfStock

## Output Format (Telegram)
```
🕷️ Scrape Complete | [timestamp]
━━━━━━━━━━━━━━━━━━
✅ X available | ❌ Y unavailable | ⚠️ Z unknown

1. [name] — $[price] — ✅/❌/⚠️
   Method: shopify-json / html-parse
   Variants: [if applicable]

✅ Results written to pipeline — Comms Claw will report automatically.
```

## Bot Handles
- Scraper Claw (you): @ScrapeFashionBot
- Research Claw: @ResearchFashion0101bot
- Communication Claw: @CommsFashionBot
