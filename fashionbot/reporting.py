"""Grouped summary reporting."""

from __future__ import annotations

from fashionbot.models import ItemCheckResult

STATUS_TITLES = {
    "available": "Available",
    "manual_check": "Manual check",
    "sold_out": "Sold out",
}


def render_summary(results: list[ItemCheckResult], *, recap: bool = False) -> str:
    selected = results if recap else [result for result in results if result.changed]
    if not selected:
        return "No availability changes."

    lines: list[str] = []
    for status in ("available", "manual_check", "sold_out"):
        grouped = [result for result in selected if result.status == status]
        if not grouped:
            continue
        lines.append(STATUS_TITLES[status])
        for result in grouped:
            old_status = f" from {result.old_status}" if result.old_status and result.old_status != result.status else ""
            link = f" - {result.purchase_link}" if result.purchase_link else ""
            price = f" - {result.price_text}" if result.price_text else ""
            lines.append(f"- {result.item_name}: {result.status}{old_status}{price}{link}")
            lines.append(f"  Evidence: {result.status_reason}")
    return "\n".join(lines)
