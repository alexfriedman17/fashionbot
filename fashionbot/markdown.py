"""Markdown mirror generation."""

from __future__ import annotations

from typing import Any

STATUS_ORDER = ("available", "manual_check", "sold_out")
STATUS_TITLES = {
    "available": "Available",
    "manual_check": "Manual check",
    "sold_out": "Sold out",
}


def render_watchlist_markdown(data: dict[str, Any]) -> str:
    lines: list[str] = [
        "# Fashion Availability Watchlist",
        "",
        "This file is generated from `watchlist.json` by the CLI. Edit the JSON source of truth instead of this mirror.",
        "",
    ]

    items = list(data.get("items", []))
    for status in STATUS_ORDER:
        grouped = [item for item in items if item.get("original_vendor_availability", "manual_check") == status]
        if not grouped:
            continue
        lines.append(f"## {STATUS_TITLES[status]}")
        lines.append("")
        for item in grouped:
            lines.extend(render_item(item))
            lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def render_item(item: dict[str, Any]) -> list[str]:
    price_target = format_price(item.get("price_target"))
    urls = item.get("original_vendor_urls", [])
    lines = [
        f"### {item.get('brand', 'Unknown')} - {item.get('product', item.get('id', 'Unknown item'))}",
        "",
        f"- Variant target: {item.get('variant', 'Unknown')}",
        f"- Size target: {item.get('size_available') or infer_size_target(item)}",
        f"- Price target: {price_target}",
        f"- Current status: {item.get('original_vendor_availability', 'manual_check')}",
        f"- Last checked: {item.get('last_checked') or 'Never'}",
    ]

    if len(urls) == 1:
        lines.append(f"- Original vendor URL: {urls[0].get('url')}")
    else:
        lines.append("- Original vendor URLs:")
        for url_info in urls:
            lines.append(f"  - {url_info.get('label', 'Product page')}: {url_info.get('url')}")

    if item.get("original_price"):
        lines.append(f"- Current price: {item['original_price']}")
    lines.append(f"- Notes: {item.get('notes') or ''}")
    return lines


def format_price(value: Any) -> str:
    if value is None or value == "":
        return "Unknown"
    if isinstance(value, (int, float)):
        return f"${value:g}"
    return str(value)


def infer_size_target(item: dict[str, Any]) -> str:
    if item.get("id") == "lego-brick-clog":
        return "M8, M9, or M10 only"
    if item.get("variant") in {"Any", "Sleet (Tech Sateen) OR Mint (Tech Sateen)"}:
        return "n/a"
    return "Unknown"
