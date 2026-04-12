# Proposed File Structure

```text
FashionBot/
  README.md
  watchlist.json
  watchlist.md
  pyproject.toml
  docs/
    PRODUCT_PRD.md
    TECHNICAL_PRD.md
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
- `fashionbot/cli.py`: command parsing and top-level run flow.
- `fashionbot/models.py`: typed watchlist and check-result models.
- `fashionbot/storage.py`: JSON load/save and validation.
- `fashionbot/checker.py`: Playwright orchestration.
- `fashionbot/classifiers.py`: generic availability classification helpers.
- `fashionbot/sites/`: source-specific selectors and extraction rules.
- `fashionbot/markdown.py`: markdown mirror generation.
- `fashionbot/reporting.py`: grouped summaries and status-change output.
- `tests/fixtures/`: small HTML examples for deterministic classifier tests.

## Build Order

1. Create the data model and seeded `watchlist.json`.
2. Add storage load/save tests.
3. Add fixture-based classifier tests.
4. Add markdown mirror generation.
5. Add Playwright live checker.
6. Add CLI recap and status-change output.
