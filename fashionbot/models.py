"""Core data models for availability checks."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

Status = Literal["available", "sold_out", "manual_check"]

AVAILABLE: Status = "available"
SOLD_OUT: Status = "sold_out"
MANUAL_CHECK: Status = "manual_check"


@dataclass(frozen=True)
class VendorUrl:
    """Exact vendor URL to check for a watched item."""

    label: str
    url: str

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "VendorUrl":
        return cls(label=str(data.get("label") or "Product page"), url=str(data["url"]))


@dataclass
class PageSignals:
    """Small, explainable set of signals captured from a product page."""

    final_url: str
    title: str = ""
    visible_text: str = ""
    buttons: list[dict[str, Any]] = field(default_factory=list)
    error: str | None = None

    @property
    def button_text(self) -> list[str]:
        return [str(button.get("text", "")).strip() for button in self.buttons if button.get("text")]

    @property
    def enabled_button_text(self) -> list[str]:
        return [
            str(button.get("text", "")).strip()
            for button in self.buttons
            if button.get("text") and bool(button.get("enabled", True))
        ]


@dataclass
class UrlCheckResult:
    """Normalized result for a single URL check."""

    item_id: str
    item_name: str
    source: str
    label: str
    url: str
    status: Status
    status_reason: str
    checked_at: str
    product_title: str = ""
    price_text: str | None = None
    variant_text: str | None = None
    purchase_link: str | None = None
    raw_signals: dict[str, Any] = field(default_factory=dict)


@dataclass
class ItemCheckResult:
    """Combined result for one watchlist item after checking all URLs."""

    item_id: str
    item_name: str
    status: Status
    old_status: str | None
    status_reason: str
    checked_at: str
    purchase_link: str | None
    price_text: str | None = None
    variant_text: str | None = None
    url_results: list[UrlCheckResult] = field(default_factory=list)

    @property
    def changed(self) -> bool:
        return self.old_status != self.status
