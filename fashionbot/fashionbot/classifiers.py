"""Conservative availability classification helpers."""

from __future__ import annotations

import re
from typing import Any

from fashionbot.models import AVAILABLE, MANUAL_CHECK, SOLD_OUT, PageSignals, Status

CHALLENGE_PATTERNS = (
    "checking if the site connection is secure",
    "verify you are human",
    "captcha",
    "cloudflare",
    "access denied",
    "bot detection",
    "blocked",
)

SOLD_OUT_PATTERNS = (
    "sold out",
    "out of stock",
    "unavailable",
)

AVAILABLE_BUTTON_PATTERNS = (
    "add to bag",
    "add to cart",
    "buy now",
)

UNCLEAR_PATTERNS = (
    "coming soon",
    "notify me",
    "waitlist",
)

PRICE_RE = re.compile(r"\$\s?\d[\d,]*(?:\.\d{2})?")


def classify_page(item: dict[str, Any], label: str, signals: PageSignals) -> tuple[Status, str]:
    """Classify a product page using only explicit visible signals."""

    if signals.error:
        return MANUAL_CHECK, signals.error

    text = normalize_text(" ".join([signals.title, signals.visible_text, " ".join(signals.button_text)]))
    enabled_buttons = [normalize_text(value) for value in signals.enabled_button_text]

    if _contains_any(text, CHALLENGE_PATTERNS):
        return MANUAL_CHECK, "Page appears blocked or challenged."

    if item.get("id") == "lego-brick-clog":
        return classify_lego_brick_clog(text)

    if _contains_any(" ".join(enabled_buttons), AVAILABLE_BUTTON_PATTERNS):
        if _contains_any(text, SOLD_OUT_PATTERNS):
            return SOLD_OUT, "Page has explicit sold-out text."
        return AVAILABLE, "Enabled purchase button is visible."

    if _contains_any(text, SOLD_OUT_PATTERNS):
        return SOLD_OUT, "Page has explicit sold-out text."

    if _contains_any(text, UNCLEAR_PATTERNS):
        return MANUAL_CHECK, "Page uses coming-soon, notify-me, waitlist, or another unclear state."

    return MANUAL_CHECK, "No explicit purchase or sold-out signal found."


def classify_lego_brick_clog(text: str) -> tuple[Status, str]:
    target_sizes = ("m8 | w10", "m9 | w11", "m10 | w12")
    missing_sizes: list[str] = []
    sold_out_sizes: list[str] = []
    maybe_available_sizes: list[str] = []

    for size in target_sizes:
        index = text.find(size)
        if index == -1:
            missing_sizes.append(size.upper())
            continue
        window = text[index : index + 180]
        if "sold out" in window:
            sold_out_sizes.append(size.upper())
        else:
            maybe_available_sizes.append(size.upper())

    if maybe_available_sizes:
        if _contains_any(text, AVAILABLE_BUTTON_PATTERNS):
            return AVAILABLE, f"Target LEGO size may be purchasable: {', '.join(maybe_available_sizes)}."
        return MANUAL_CHECK, f"Target LEGO size lacks sold-out text but no explicit purchase signal was found: {', '.join(maybe_available_sizes)}."

    if sold_out_sizes and not missing_sizes:
        return SOLD_OUT, f"All target LEGO sizes are explicitly sold out: {', '.join(sold_out_sizes)}."

    if sold_out_sizes:
        return MANUAL_CHECK, f"Some LEGO target sizes were sold out, but others were missing from the page: {', '.join(missing_sizes)}."

    return MANUAL_CHECK, "No target LEGO sizes were found on the page."


def extract_price_text(text: str) -> str | None:
    matches = [re.sub(r"\s+", "", match.group(0)) for match in PRICE_RE.finditer(text)]
    unique_matches = list(dict.fromkeys(matches))
    if len(unique_matches) != 1:
        return None
    return unique_matches[0]


def normalize_text(value: str) -> str:
    return re.sub(r"\s+", " ", value or "").strip().lower()


def _contains_any(value: str, patterns: tuple[str, ...]) -> bool:
    return any(pattern in value for pattern in patterns)
