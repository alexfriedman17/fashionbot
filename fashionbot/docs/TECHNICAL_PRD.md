# Technical PRD: Fashion Availability Agent

## Recommended Stack

- Python for the CLI and data handling.
- Playwright for browser-based checks of dynamic ecommerce pages.
- Pytest for unit and fixture-based classification tests.
- JSON for canonical item state.
- Markdown for the generated human-readable mirror.

## Runtime Model

The checker runs locally on demand:

```powershell
python -m fashionbot check
python -m fashionbot check --recap
```

Scheduling can be added later after the live checks are reliable.

## Data Model

Recommended item fields:

```json
{
  "id": "topologie-bomber-strap",
  "brand": "Topologie",
  "product": "Bomber Strap",
  "variant": "Any",
  "price_target": 75,
  "price_available": null,
  "original_vendor_availability": "manual_check",
  "original_price": null,
  "link_to_suggested_purchase": "https://topologie.com/products/bomber-strap",
  "size_available": null,
  "color_available": null,
  "last_checked": null,
  "notes": "",
  "original_vendor_urls": [
    {
      "label": "Product page",
      "url": "https://topologie.com/products/bomber-strap"
    }
  ]
}
```

## Check Pipeline

Detailed scraper rules live in `docs/SCRAPING_APPROACH.md`.

1. Load and validate `watchlist.json`.
2. Open each exact original vendor URL with Playwright.
3. Wait for visible product-page content.
4. Extract explicit page signals: title, price, variant text, stock button text, disabled states, sold-out messages, and challenge/blocking text.
5. Classify the item as `available`, `sold_out`, or `manual_check`.
6. Compare current status with the previous saved status.
7. Update `watchlist.json`.
8. Regenerate `watchlist.md`.
9. Print status-change summary, or full recap when requested.

## Conservative Classification

Use source-specific selectors when reliable, but keep a generic fallback based on visible product area text and action buttons.

Positive availability examples:

- `Add to Bag`
- `Add to Cart`
- `Buy Now`
- Enabled purchase button for the selected or target variant.

Sold-out examples:

- `Sold Out`
- `Out of Stock`
- `Unavailable`
- Disabled purchase button paired with sold-out text.

Manual-check examples:

- Cloudflare, captcha, bot challenge, or access denied.
- Coming soon or waitlist states.
- Missing product form.
- Variant mismatch.
- Redirect to an unexpected page.
- Page loads but status text is ambiguous.

## Testing Strategy

- Unit test JSON loading, validation, saving, and markdown generation.
- Unit test status-change comparison.
- Fixture test classifier behavior for available, sold-out, blocked, coming-soon, ambiguous, and missing-status HTML.
- Add one manual smoke test command for live browser checks before relying on all items.

## Future Extensions

- Scheduled runs.
- Email or webhook update channels.
- Poshmark exact URL or saved-search support.
- Persistent browser profile setup guide.
- Optional dashboard.
