"""Command-line interface for FashionBot."""

from __future__ import annotations

import argparse
from pathlib import Path

from fashionbot.checker import BrowserBackendUnavailable, check_watchlist
from fashionbot.config import (
    DEFAULT_BROWSER_BACKEND,
    DEFAULT_MARKDOWN_PATH,
    DEFAULT_PROFILE_DIR,
    DEFAULT_TIMEOUT_MS,
    DEFAULT_TIMEZONE,
    DEFAULT_WATCHLIST_PATH,
)
from fashionbot.markdown import render_watchlist_markdown
from fashionbot.reporting import render_summary
from fashionbot.storage import load_watchlist, save_watchlist


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="fashionbot")
    subparsers = parser.add_subparsers(dest="command", required=True)

    check_parser = subparsers.add_parser("check", help="Check watchlist availability")
    check_parser.add_argument("--watchlist", default=DEFAULT_WATCHLIST_PATH, help="Path to watchlist JSON")
    check_parser.add_argument("--markdown", default=DEFAULT_MARKDOWN_PATH, help="Path to markdown mirror")
    check_parser.add_argument("--browser", default=DEFAULT_BROWSER_BACKEND, choices=("playwright", "blueprint"), help="Browser backend")
    check_parser.add_argument("--headless", action="store_true", help="Run Playwright headless")
    check_parser.add_argument("--profile-dir", default=DEFAULT_PROFILE_DIR, help="Persistent browser profile directory")
    check_parser.add_argument("--timeout-ms", type=int, default=DEFAULT_TIMEOUT_MS, help="Per-page timeout in milliseconds")
    check_parser.add_argument("--timezone", default=DEFAULT_TIMEZONE, help="IANA timezone for timestamps")
    check_parser.add_argument("--recap", action="store_true", help="Print all statuses instead of only changes")
    check_parser.add_argument("--dry-run", action="store_true", help="Do not write watchlist or markdown updates")
    check_parser.add_argument("--no-markdown", action="store_true", help="Do not regenerate watchlist.md")
    check_parser.set_defaults(func=run_check)
    return parser


def run_check(args: argparse.Namespace) -> int:
    data = load_watchlist(args.watchlist)
    try:
        results = check_watchlist(
            data,
            backend=args.browser,
            headless=args.headless,
            profile_dir=args.profile_dir,
            timeout_ms=args.timeout_ms,
            timezone=args.timezone,
        )
    except BrowserBackendUnavailable as exc:
        print(f"Browser backend unavailable: {exc}")
        return 2

    if not args.dry_run:
        save_watchlist(data, args.watchlist)
        if not args.no_markdown:
            Path(args.markdown).write_text(render_watchlist_markdown(data), encoding="utf-8")

    print(render_summary(results, recap=args.recap))
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))
