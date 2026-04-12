# Fashion Availability Agent

Barebones project outline for a local fashion resale availability checker.

The first version checks exact original-vendor product URLs, stores structured state in `watchlist.json`, mirrors it to `watchlist.md`, and reports only status changes unless a full recap is requested.

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
- `docs/FILE_STRUCTURE.md`: proposed file tree and responsibilities.

## Proposed Commands

```powershell
python -m fashionbot check
python -m fashionbot check --recap
python -m pytest
```

## Source Of Truth

`watchlist.json` is canonical. `watchlist.md` is a generated human-readable mirror and should not be manually edited once the app exists.
