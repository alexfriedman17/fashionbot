"""Generic source extraction and classification."""

from __future__ import annotations

from typing import Any

from fashionbot.classifiers import classify_page, extract_price_text
from fashionbot.models import PageSignals


def classify_signals(item: dict[str, Any], label: str, signals: PageSignals) -> tuple[str, str, str | None]:
    status, reason = classify_page(item, label, signals)
    price_text = extract_price_text(signals.visible_text)
    return status, reason, price_text
