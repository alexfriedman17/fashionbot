# Initial Scraping Approach

Last updated: 2026-04-12

## Purpose

This document defines the first scraper implementation for the Fashion Availability Agent. The scraper should answer one question for each watched item: does the exact original vendor page explicitly show that the item or target variant is available, sold out, or unclear?

## Non-Goals

- Do not scrape Poshmark in v1.
- Do not auto-purchase items.
- Do not guess availability from product images, price text, related items, or search results.
- Do not bypass Cloudflare, captcha, access-denied pages, or other anti-bot controls.
- Do not classify a variant as available unless the live page explicitly supports that exact target or the watch item says `Any`.

## Scraper Runtime

Use Playwright with a headed Chromium browser for the first version.

Recommended default behavior:

- Launch headed browser mode for easier debugging.
- Use a persistent local browser profile directory such as `.browser-profile/`.
- Reuse cookies and normal browsing state across runs.
- Keep request volume low: one exact page load per watched URL, with small delays between items.
- If a page presents a bot challenge, captcha, access denied state, unexpected redirect, or unclear UI, return `manual_check`.

The persistent profile is for ordinary user-session continuity only. It is not a Cloudflare or captcha bypass strategy.

## Scraper Contract

Each source-specific scraper should return a normalized check result:

```json
{
  "item_id": "topologie-bomber-strap",
  "source": "original_vendor",
  "url": "https://topologie.com/products/bomber-strap",
  "status": "manual_check",
  "status_reason": "No explicit purchase or sold-out signal found.",
  "product_title": "Bomber Strap",
  "price_text": null,
  "variant_text": null,
  "purchase_link": "https://topologie.com/products/bomber-strap",
  "checked_at": "2026-04-12T00:00:00-04:00",
  "raw_signals": {
    "button_text": [],
    "sold_out_text": [],
    "challenge_text": []
  }
}
```

Allowed statuses:

- `available`
- `sold_out`
- `manual_check`

## Classification Rules

Mark `available` only when:

- The page is the expected product page.
- The target item or variant is visible or selected.
- A purchase button is enabled and uses explicit text such as `Add to Bag`, `Add to Cart`, or `Buy Now`.

Mark `sold_out` only when:

- The page is the expected product page.
- The page explicitly shows text such as `Sold Out`, `Out of Stock`, or `Unavailable`.
- A disabled purchase button is paired with explicit sold-out or unavailable text.

Mark `manual_check` when:

- A Cloudflare, captcha, bot challenge, access denied, or security-check page appears.
- The product page is missing, redirected, or not clearly the expected item.
- The product UI loads but no explicit stock status is found.
- The target variant cannot be matched.
- The page says `Coming Soon`, `Waitlist`, `Notify Me`, or similar.
- The scraper hits a timeout, network error, or JavaScript-rendering failure.

## Source-Specific Notes

### Topologie

Initial watched URLs:

- `https://topologie.com/products/bomber-strap`
- `https://topologie.com/products/scrunchie-pocket-wrist`
- `https://topologie.com/products/bungee-wrist-strap-sleet-tech-sateen`
- `https://topologie.com/products/bungee-wrist-strap?_pos=1&_sid=4759fef48&_ss=r&variant=44881325981869`

Implementation notes:

- Try exact product-page checks first.
- Extract visible product title, selected color or variant text, price text, and primary purchase button text.
- For `Any` variant targets, availability can be true if any visible purchasable option is explicitly available.
- For `Bungee Wrist Strap`, treat Sleet and Mint as one watch item. Either exact URL may satisfy the item if that variant explicitly shows availability.
- If the variant URL does not clearly select Mint, return `manual_check` instead of guessing.

### Coachtopia / Coach

Initial watched URLs:

- `https://www.coach.com/products/coachtopia/small-slouchy-shoulder-bag-in-upcrafted-patchwork/CFF99-Z6Q.html`
- `https://www.coach.com/products/coachtopia/alterego-slouchy-shoulder-bag-in-upcrafted-leather/CBE00.html`

Implementation notes:

- Use browser-rendered page checks first.
- Extract visible product title, price text, color or variant text, and primary purchase button text.
- The current watchlist target fields are unknown, so classify only the exact product page, not inferred colors or sizes.
- If the page shows coming-soon, waitlist, unavailable, or unclear purchase state, return `manual_check` unless sold-out text is explicit.

## Page Signal Collection

Collect these signals before classification:

- Final URL after redirects.
- Page title.
- Main visible text near the product area.
- Primary button labels and whether buttons are enabled.
- Visible price text.
- Visible variant or color text.
- Challenge/blocking text.
- Error or timeout details.

Keep raw signals short. Store enough to explain the decision, not a full page dump.

## Update Flow

1. Load `watchlist.json`.
2. For each item, check all `original_vendor_urls`.
3. For multi-URL items, combine the URL results conservatively:
   - If any target URL is explicitly `available`, the item is `available`.
   - Else if every target URL is explicitly `sold_out`, the item is `sold_out`.
   - Else the item is `manual_check`.
4. Compare the new item status to the previous `original_vendor_availability`.
5. Update `price_available`, `original_price`, `link_to_suggested_purchase`, `size_available`, `color_available`, `last_checked`, and `notes` only when explicitly supported by the check result.
6. Save `watchlist.json`.
7. Regenerate `watchlist.md`.
8. Print changed items, grouped by status. Print all items only with `--recap`.

## Manual Smoke Checklist

Before relying on the scraper, run one live browser check for each vendor:

- Confirm the browser opens visibly.
- Confirm the product URL loads.
- Confirm title and button text are captured.
- Confirm blocked or challenged pages return `manual_check`.
- Confirm unchanged statuses do not print update noise unless `--recap` is used.

## First Implementation Steps

1. Build the normalized check-result model.
2. Add a generic visible-text classifier with fixture tests.
3. Add Playwright page loading with timeout and screenshot-on-error disabled by default.
4. Add Topologie extraction.
5. Add Coach extraction.
6. Add multi-URL item combination for the Bungee Wrist Strap.
7. Wire results into JSON update and markdown regeneration.
