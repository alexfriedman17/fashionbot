"""Static HTML dashboard generation."""

from __future__ import annotations

from collections import Counter
from datetime import datetime
from html import escape
from typing import Any

STATUS_ORDER = ("available", "manual_check", "sold_out")
STATUS_TITLES = {
    "available": "Available",
    "manual_check": "Manual check",
    "sold_out": "Sold out",
}
STATUS_RANK = {status: index for index, status in enumerate(STATUS_ORDER)}


def render_dashboard_html(data: dict[str, Any]) -> str:
    items = sorted(
        list(data.get("items", [])),
        key=lambda item: (
            STATUS_RANK.get(str(item.get("original_vendor_availability", "manual_check")), len(STATUS_ORDER)),
            str(item.get("brand", "")).casefold(),
            str(item.get("product", "")).casefold(),
        ),
    )
    counts = Counter(str(item.get("original_vendor_availability", "manual_check")) for item in items)
    latest_check = newest_last_checked(items)

    rows = "\n".join(render_item_row(item) for item in items)
    if not rows:
        rows = '<tr><td colspan="9" class="empty">No items are configured yet.</td></tr>'

    summary_items = "\n".join(
        f"""
        <div class="metric metric-{escape_attr(status)}">
          <span class="metric-value">{counts.get(status, 0)}</span>
          <span class="metric-label">{escape_html(STATUS_TITLES[status])}</span>
        </div>""".rstrip()
        for status in STATUS_ORDER
    )

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta http-equiv="refresh" content="300">
  <title>Fashion Availability</title>
  <style>
    :root {{
      color-scheme: light;
      --page: #f7f8fa;
      --surface: #ffffff;
      --ink: #191a1f;
      --muted: #5f6368;
      --line: #d9dde3;
      --available: #176b3a;
      --available-bg: #e8f6ee;
      --manual: #735c00;
      --manual-bg: #fff6c7;
      --sold: #a3262a;
      --sold-bg: #fde8e8;
      --link: #005ea8;
    }}

    * {{
      box-sizing: border-box;
    }}

    body {{
      margin: 0;
      background: var(--page);
      color: var(--ink);
      font-family: Arial, Helvetica, sans-serif;
      font-size: 16px;
      line-height: 1.5;
      letter-spacing: 0;
    }}

    main {{
      width: min(1180px, calc(100% - 32px));
      margin: 0 auto;
      padding: 32px 0 48px;
    }}

    header {{
      display: grid;
      gap: 8px;
      margin-bottom: 24px;
    }}

    h1 {{
      margin: 0;
      font-size: 2rem;
      line-height: 1.15;
    }}

    .updated {{
      margin: 0;
      color: var(--muted);
    }}

    .summary {{
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 12px;
      margin-bottom: 18px;
    }}

    .metric {{
      min-height: 86px;
      display: grid;
      align-content: center;
      gap: 2px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: var(--surface);
      padding: 16px;
    }}

    .metric-value {{
      font-size: 1.8rem;
      font-weight: 700;
      line-height: 1;
    }}

    .metric-label {{
      color: var(--muted);
      font-weight: 700;
    }}

    .metric-available {{
      border-color: #b6dfc6;
      background: var(--available-bg);
    }}

    .metric-manual_check {{
      border-color: #eadb79;
      background: var(--manual-bg);
    }}

    .metric-sold_out {{
      border-color: #f0b7b8;
      background: var(--sold-bg);
    }}

    .table-wrap {{
      overflow-x: auto;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: var(--surface);
    }}

    table {{
      width: 100%;
      min-width: 980px;
      border-collapse: collapse;
    }}

    th,
    td {{
      padding: 14px 16px;
      border-bottom: 1px solid var(--line);
      text-align: left;
      vertical-align: top;
    }}

    th {{
      background: #eceff3;
      color: #2d3035;
      font-size: 0.9rem;
      font-weight: 700;
    }}

    tr:last-child td {{
      border-bottom: 0;
    }}

    .item-name {{
      font-weight: 700;
    }}

    .subtle {{
      color: var(--muted);
    }}

    .status {{
      display: inline-flex;
      align-items: center;
      min-height: 28px;
      border-radius: 8px;
      padding: 3px 10px;
      font-weight: 700;
      white-space: nowrap;
    }}

    .status-available {{
      background: var(--available-bg);
      color: var(--available);
    }}

    .status-manual_check {{
      background: var(--manual-bg);
      color: var(--manual);
    }}

    .status-sold_out {{
      background: var(--sold-bg);
      color: var(--sold);
    }}

    a {{
      color: var(--link);
      font-weight: 700;
    }}

    .empty {{
      padding: 28px 16px;
      color: var(--muted);
      text-align: center;
    }}

    @media (max-width: 720px) {{
      main {{
        width: min(100% - 24px, 1180px);
        padding-top: 22px;
      }}

      h1 {{
        font-size: 1.6rem;
      }}

      .summary {{
        grid-template-columns: 1fr;
      }}
    }}
  </style>
</head>
<body>
  <main>
    <header>
      <h1>Fashion Availability</h1>
      <p class="updated">Latest check: {escape_html(latest_check)}</p>
    </header>
    <section class="summary" aria-label="Status summary">
      {summary_items}
    </section>
    <div class="table-wrap">
      <table>
        <thead>
          <tr>
            <th>Status</th>
            <th>Item</th>
            <th>Target</th>
            <th>Available variant</th>
            <th>Current price</th>
            <th>Target price</th>
            <th>Last checked</th>
            <th>Notes</th>
            <th>Link</th>
          </tr>
        </thead>
        <tbody>
          {rows}
        </tbody>
      </table>
    </div>
  </main>
</body>
</html>
"""


def render_item_row(item: dict[str, Any]) -> str:
    status = str(item.get("original_vendor_availability") or "manual_check")
    status_title = STATUS_TITLES.get(status, status.replace("_", " ").title())
    item_name = f"{item.get('brand', 'Unknown')} - {item.get('product', item.get('id', 'Unknown item'))}"
    target = str(item.get("variant") or "Unknown")
    available_variant = format_available_variant(item)
    current_price = format_price(item.get("original_price") or item.get("price_available"))
    target_price = format_price(item.get("price_target"))
    last_checked = format_timestamp(item.get("last_checked"))
    notes = str(item.get("notes") or "")
    link = best_purchase_link(item)
    link_cell = f'<a href="{escape_attr(link)}">Open</a>' if link else '<span class="subtle">Not set</span>'

    return f"""<tr>
            <td><span class="status status-{escape_attr(status)}">{escape_html(status_title)}</span></td>
            <td><span class="item-name">{escape_html(item_name)}</span></td>
            <td>{escape_html(target)}</td>
            <td>{escape_html(available_variant)}</td>
            <td>{escape_html(current_price)}</td>
            <td>{escape_html(target_price)}</td>
            <td>{escape_html(last_checked)}</td>
            <td>{escape_html(notes)}</td>
            <td>{link_cell}</td>
          </tr>"""


def best_purchase_link(item: dict[str, Any]) -> str:
    if item.get("link_to_suggested_purchase"):
        return str(item["link_to_suggested_purchase"])
    urls = item.get("original_vendor_urls") or []
    if urls and isinstance(urls[0], dict) and urls[0].get("url"):
        return str(urls[0]["url"])
    return ""


def format_available_variant(item: dict[str, Any]) -> str:
    parts = [str(value) for value in (item.get("size_available"), item.get("color_available")) if value]
    if parts:
        return ", ".join(parts)
    if item.get("original_vendor_availability") == "available":
        return "Available"
    return "Not confirmed"


def format_price(value: Any) -> str:
    if value is None or value == "":
        return "Unknown"
    if isinstance(value, (int, float)):
        return f"${value:g}"
    return str(value)


def newest_last_checked(items: list[dict[str, Any]]) -> str:
    values = [str(item.get("last_checked") or "") for item in items if item.get("last_checked")]
    if not values:
        return "Never"
    return format_timestamp(max(values))


def format_timestamp(value: Any) -> str:
    if not value:
        return "Never"
    timestamp = str(value)
    try:
        parsed = datetime.fromisoformat(timestamp)
    except ValueError:
        return timestamp
    return parsed.strftime("%Y-%m-%d %I:%M %p %z").replace(" 0", " ")


def escape_html(value: Any) -> str:
    return escape(str(value), quote=False)


def escape_attr(value: Any) -> str:
    return escape(str(value), quote=True)
