# Fashion Availability Agent

Local fashion availability checker for exact original-vendor product URLs.

The CLI reads `watchlist.json`, checks each item conservatively, regenerates `watchlist.md`, and reports status changes unless a full recap is requested.

## Current Scope

- Original vendor pages only.
- Exact URLs only.
- Conservative availability classification: `available`, `sold_out`, or `manual_check`.
- Local command-line summaries first.
- No Poshmark checks in v1.
- No Cloudflare or captcha bypassing; blocked or unclear pages become `manual_check`.

## Key Docs

- `docs/PRODUCT_PRD.md`: product behavior and success criteria.
- `docs/TECHNICAL_PRD.md`: implementation approach and constraints.
- `docs/SCRAPING_APPROACH.md`: first-pass scraper contract, classification rules, and site notes.
- `docs/BROWSER_BACKENDS.md`: Playwright and Blueprint MCP backend notes.
- `docs/SITE_CHECKING_STRATEGY.md`: per-site guidance for HTTP, Playwright, Blueprint, and manual-check fallbacks.
- `docs/FILE_STRUCTURE.md`: proposed file tree and responsibilities.

## Common Commands

```powershell
python -m pip install -e .[dev]
python -m playwright install chromium
python -m fashionbot check
python -m fashionbot check --recap
python -m fashionbot check --dry-run --recap
python -m fashionbot check --browser blueprint
python -m pytest
```

`--browser playwright` is the working local backend. `--browser blueprint` is reserved for a future MCP-backed browser flow and reports setup guidance unless Blueprint MCP is registered with the agent host.

## Source Of Truth

`watchlist.json` is canonical. `watchlist.md` is a generated human-readable mirror and should not be manually edited once the app exists.
