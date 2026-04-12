"""Watchlist JSON load/save helpers."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_watchlist(path: str | Path = "watchlist.json") -> dict[str, Any]:
    watchlist_path = Path(path)
    data = json.loads(watchlist_path.read_text(encoding="utf-8"))
    validate_watchlist(data)
    return data


def save_watchlist(data: dict[str, Any], path: str | Path = "watchlist.json") -> None:
    validate_watchlist(data)
    watchlist_path = Path(path)
    watchlist_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def validate_watchlist(data: dict[str, Any]) -> None:
    if not isinstance(data, dict):
        raise ValueError("watchlist must be a JSON object")
    if "items" not in data or not isinstance(data["items"], list):
        raise ValueError("watchlist must contain an items list")

    seen_ids: set[str] = set()
    for index, item in enumerate(data["items"]):
        if not isinstance(item, dict):
            raise ValueError(f"watchlist item {index} must be an object")

        item_id = item.get("id")
        if not item_id or not isinstance(item_id, str):
            raise ValueError(f"watchlist item {index} must have a string id")
        if item_id in seen_ids:
            raise ValueError(f"duplicate watchlist item id: {item_id}")
        seen_ids.add(item_id)

        urls = item.get("original_vendor_urls")
        if not isinstance(urls, list) or not urls:
            raise ValueError(f"watchlist item {item_id} must have original_vendor_urls")
        for url_index, url_info in enumerate(urls):
            if not isinstance(url_info, dict) or not url_info.get("url"):
                raise ValueError(f"watchlist item {item_id} URL {url_index} must contain a url")
