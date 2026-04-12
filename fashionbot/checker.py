"""Browser checker orchestration."""

from __future__ import annotations

import re
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

from fashionbot.models import AVAILABLE, MANUAL_CHECK, SOLD_OUT, ItemCheckResult, PageSignals, UrlCheckResult
from fashionbot.sites.generic import classify_signals


class BrowserBackendUnavailable(RuntimeError):
    """Raised when the requested browser backend is not available locally."""


def check_watchlist(
    data: dict[str, Any],
    *,
    backend: str = "playwright",
    headless: bool = False,
    profile_dir: str | Path = ".browser-profile",
    timeout_ms: int = 30_000,
    timezone: str = "America/New_York",
) -> list[ItemCheckResult]:
    if backend == "blueprint":
        raise BrowserBackendUnavailable(
            "Blueprint MCP is not registered in this Codex session. Install the Blueprint Chrome extension, "
            "install @railsblueprint/blueprint-mcp, and add it as an MCP server to the agent host before "
            "using Blueprint-driven browsing. Use --browser playwright for the local CLI today."
        )
    if backend != "playwright":
        raise BrowserBackendUnavailable(f"Unsupported browser backend: {backend}")

    try:
        from playwright.sync_api import Error as PlaywrightError
        from playwright.sync_api import sync_playwright
    except ImportError as exc:
        raise BrowserBackendUnavailable(
            "Playwright is not installed. Run `python -m pip install -e .` and "
            "`python -m playwright install chromium`, then retry."
        ) from exc

    checked_at = datetime.now(ZoneInfo(timezone)).isoformat(timespec="seconds")
    results: list[ItemCheckResult] = []
    profile_path = str(Path(profile_dir))

    with sync_playwright() as playwright:
        context = playwright.chromium.launch_persistent_context(
            profile_path,
            headless=headless,
            viewport={"width": 1440, "height": 1100},
            locale="en-US",
        )
        try:
            for item in data.get("items", []):
                url_results: list[UrlCheckResult] = []
                for url_info in item.get("original_vendor_urls", []):
                    try:
                        url_result = check_url(context, item, url_info, checked_at=checked_at, timeout_ms=timeout_ms)
                    except PlaywrightError as exc:
                        url_result = error_result(item, url_info, checked_at, f"Playwright error: {exc}")
                    url_results.append(url_result)

                item_result = combine_item_results(item, url_results, checked_at)
                apply_item_result(item, item_result)
                results.append(item_result)
        finally:
            context.close()

    return results


def check_url(context: Any, item: dict[str, Any], url_info: dict[str, Any], *, checked_at: str, timeout_ms: int) -> UrlCheckResult:
    url = str(url_info["url"])
    label = str(url_info.get("label") or "Product page")
    item_name = format_item_name(item)
    page = context.new_page()
    try:
        page.goto(url, wait_until="domcontentloaded", timeout=timeout_ms)
        handle_post_load_popups(page, item)
        signals = collect_page_signals(page)
    except Exception as exc:  # Playwright throws backend-specific subclasses.
        signals = PageSignals(final_url=url, error=f"Could not load page: {exc}")
    finally:
        page.close()

    status, reason, price_text = classify_signals(item, label, signals)
    return UrlCheckResult(
        item_id=str(item["id"]),
        item_name=item_name,
        source="original_vendor",
        label=label,
        url=url,
        status=status,
        status_reason=reason,
        checked_at=checked_at,
        product_title=signals.title,
        price_text=price_text,
        purchase_link=signals.final_url or url,
        raw_signals={
            "final_url": signals.final_url,
            "button_text": signals.button_text[:12],
            "enabled_button_text": signals.enabled_button_text[:12],
            "target_button_text": target_button_text(item, signals),
            "error": signals.error,
        },
    )


def collect_page_signals(page: Any) -> PageSignals:
    wait_for_page_settle(page)
    title = retry_page_read(page, page.title, "")
    final_url = page.url
    visible_text = retry_page_read(page, lambda: page.locator("body").inner_text(timeout=5000), "")
    buttons = retry_page_read(page, lambda: collect_button_signals_for_page(page), [])
    return PageSignals(final_url=final_url, title=title, visible_text=visible_text, buttons=buttons)


def wait_for_page_settle(page: Any) -> None:
    try:
        page.wait_for_load_state("domcontentloaded", timeout=5000)
    except Exception:
        pass


def retry_page_read(page: Any, read: Any, default: Any) -> Any:
    for _ in range(3):
        try:
            return read()
        except Exception:
            page.wait_for_timeout(1000)
    return default


def collect_button_signals_for_page(page: Any) -> list[dict[str, Any]]:
    return page.locator("button, [role=button], input[type=submit], input[type=button]").evaluate_all(
        """elements => elements.slice(0, 100).map((el) => {
            const text = (el.innerText || el.value || el.getAttribute('aria-label') || '').trim();
            const disabled = Boolean(el.disabled) || el.getAttribute('aria-disabled') === 'true';
            return { text, enabled: !disabled };
        }).filter((item) => item.text);
        """
    )


def handle_post_load_popups(page: Any, item: dict[str, Any]) -> None:
    """Dismiss known non-purchase popups before scraping product signals."""

    page.wait_for_timeout(3000)
    if item.get("id") == "lego-brick-clog":
        dismiss_lego_destination_popup(page)
    page.wait_for_timeout(1000)


def dismiss_lego_destination_popup(page: Any) -> None:
    """Close LEGO's retail/games destination choice if it appears."""

    dialog_selectors = ("[role=dialog]", "dialog", "[aria-modal='true']")
    retail_games_re = re.compile(r"(retail|shop).*(game|play)|(game|play).*(retail|shop)", re.IGNORECASE | re.DOTALL)
    preferred_labels = (
        "Continue to LEGO.com",
        "Continue to LEGO Shop",
        "Continue to LEGO Retail",
        "Continue to shop",
        "Continue shopping",
        "LEGO.com",
        "LEGO Shop",
    )

    for selector in dialog_selectors:
        dialogs = page.locator(selector)
        try:
            count = min(dialogs.count(), 5)
        except Exception:
            continue

        for index in range(count):
            dialog = dialogs.nth(index)
            try:
                dialog_text = dialog.inner_text(timeout=750)
            except Exception:
                continue

            if not retail_games_re.search(dialog_text):
                continue

            for label in preferred_labels:
                button = dialog.get_by_role("button", name=re.compile(re.escape(label), re.IGNORECASE))
                try:
                    if button.count() > 0:
                        button.first.click(timeout=2000)
                        return
                except Exception:
                    continue

            buttons = dialog.locator("button")
            try:
                button_count = min(buttons.count(), 10)
            except Exception:
                continue
            for button_index in range(button_count):
                button = buttons.nth(button_index)
                try:
                    text = button.inner_text(timeout=500)
                except Exception:
                    continue
                if re.search(r"retail|shop|lego\.com", text, re.IGNORECASE):
                    button.click(timeout=2000)
                    return


def error_result(item: dict[str, Any], url_info: dict[str, Any], checked_at: str, reason: str) -> UrlCheckResult:
    url = str(url_info.get("url") or "")
    label = str(url_info.get("label") or "Product page")
    return UrlCheckResult(
        item_id=str(item["id"]),
        item_name=format_item_name(item),
        source="original_vendor",
        label=label,
        url=url,
        status=MANUAL_CHECK,
        status_reason=reason,
        checked_at=checked_at,
        purchase_link=url,
        raw_signals={"error": reason},
    )


def combine_item_results(item: dict[str, Any], url_results: list[UrlCheckResult], checked_at: str) -> ItemCheckResult:
    old_status = item.get("original_vendor_availability")
    available_result = next((result for result in url_results if result.status == AVAILABLE), None)
    if available_result:
        return ItemCheckResult(
            item_id=str(item["id"]),
            item_name=format_item_name(item),
            status=AVAILABLE,
            old_status=old_status,
            status_reason=available_result.status_reason,
            checked_at=checked_at,
            purchase_link=available_result.purchase_link,
            price_text=available_result.price_text,
            variant_text=result_label_as_variant(available_result.label),
            url_results=url_results,
        )

    if url_results and all(result.status == SOLD_OUT for result in url_results):
        first = url_results[0]
        return ItemCheckResult(
            item_id=str(item["id"]),
            item_name=format_item_name(item),
            status=SOLD_OUT,
            old_status=old_status,
            status_reason="All checked URLs are explicitly sold out.",
            checked_at=checked_at,
            purchase_link=first.purchase_link,
            price_text=first.price_text,
            url_results=url_results,
        )

    manual_reasons = "; ".join(f"{result.label}: {result.status_reason}" for result in url_results)
    return ItemCheckResult(
        item_id=str(item["id"]),
        item_name=format_item_name(item),
        status=MANUAL_CHECK,
        old_status=old_status,
        status_reason=manual_reasons or "No URLs were checked.",
        checked_at=checked_at,
        purchase_link=item.get("link_to_suggested_purchase"),
        url_results=url_results,
    )


def apply_item_result(item: dict[str, Any], result: ItemCheckResult) -> None:
    item["original_vendor_availability"] = result.status
    item["last_checked"] = result.checked_at
    if result.price_text:
        item["original_price"] = result.price_text
        item["price_available"] = result.price_text
    if result.purchase_link:
        item["link_to_suggested_purchase"] = result.purchase_link
    item["color_available"] = result.variant_text
    item["notes"] = result.status_reason


def result_label_as_variant(label: str | None) -> str | None:
    if not label or label == "Product page":
        return None
    return label


def format_item_name(item: dict[str, Any]) -> str:
    return f"{item.get('brand', 'Unknown')} - {item.get('product', item.get('id', 'Unknown item'))}"


def target_button_text(item: dict[str, Any], signals: PageSignals) -> list[str]:
    if item.get("id") != "lego-brick-clog":
        return []
    needles = ("M8", "M9", "M10")
    return [text for text in signals.button_text if any(needle in text for needle in needles)]


def results_as_dicts(results: list[ItemCheckResult]) -> list[dict[str, Any]]:
    return [asdict(result) for result in results]
