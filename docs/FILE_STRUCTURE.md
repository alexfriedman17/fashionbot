# Project File Structure

```text
FashionBot/
  .gitignore
  README.md
  watchlist.json
  watchlist.md
  checkout_profile.example.json
  pyproject.toml
  blockdiagrams/
    claw-flowcharts.mermaid
    inter-claw-messaging.mermaid
    pipeline-flow.mermaid
  docs/
    PRODUCT_PRD.md
    TECHNICAL_PRD.md
    SCRAPING_APPROACH.md
    BROWSER_BACKENDS.md
    SITE_CHECKING_STRATEGY.md
    FILE_STRUCTURE.md
  fashionbot/
    __init__.py
    __main__.py
    cli.py
    config.py
    models.py
    storage.py
    checker.py
    classifiers.py
    markdown.py
    reporting.py
    sites/
      __init__.py
      generic.py
      topologie.py
      coach.py
      lego.py
  tests/
    test_classifiers.py
    test_markdown.py
    test_storage.py
    fixtures/
      available.html
      sold_out.html
      blocked.html
      ambiguous.html
```

## Responsibilities

- `watchlist.json`: canonical item state.
- `watchlist.md`: generated human-readable mirror.
- `checkout_profile.example.json`: safe checkout-prep schema without raw card data.
- `blockdiagrams/`: architecture and OpenClaw planning diagrams.
- `docs/SCRAPING_APPROACH.md`: first-pass browser scraping contract and classification guidance.
- `docs/SITE_CHECKING_STRATEGY.md`: per-site backend choice and fallback guidance.
- `fashionbot/cli.py`: command parsing and top-level run flow.
- `fashionbot/models.py`: typed watchlist and check-result models.
- `fashionbot/storage.py`: JSON load/save and validation.
- `fashionbot/checker.py`: Playwright orchestration.
- `fashionbot/classifiers.py`: generic availability classification helpers.
- `fashionbot/sites/`: source-specific selectors and extraction rules.
- `fashionbot/markdown.py`: markdown mirror generation.
- `fashionbot/reporting.py`: grouped summaries and status-change output.
- `tests/fixtures/`: small HTML examples for deterministic classifier tests.

## Current Build Priorities

1. Keep `watchlist.json` as the canonical state file.
2. Use the Playwright CLI for Topologie and LEGO checks.
3. Add an HTTP-first Coach checker before relying on Coach browser screenshots.
4. Keep Blueprint MCP as a future backend until it is registered with the agent host.
5. Run `python -m pytest` before pushing.
