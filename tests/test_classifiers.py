from fashionbot.classifiers import classify_page
from fashionbot.models import AVAILABLE, MANUAL_CHECK, SOLD_OUT, PageSignals


def test_classifies_enabled_purchase_button_as_available():
    status, reason = classify_page(
        {"id": "topologie-bomber-strap"},
        "Product page",
        PageSignals(final_url="https://example.com", title="Bomber Strap", visible_text="$75", buttons=[{"text": "Add to Bag", "enabled": True}]),
    )

    assert status == AVAILABLE
    assert "Enabled purchase button" in reason


def test_classifies_sold_out_text_as_sold_out():
    status, reason = classify_page(
        {"id": "topologie-bomber-strap"},
        "Product page",
        PageSignals(final_url="https://example.com", visible_text="Bomber Strap $75 Sold Out", buttons=[{"text": "Sold Out", "enabled": False}]),
    )

    assert status == SOLD_OUT
    assert "sold-out" in reason


def test_explicit_sold_out_beats_notify_me_text():
    status, reason = classify_page(
        {"id": "topologie-bomber-strap"},
        "Product page",
        PageSignals(final_url="https://example.com", visible_text="Notify me when available. Sold Out"),
    )

    assert status == SOLD_OUT
    assert "sold-out" in reason


def test_classifies_challenge_as_manual_check():
    status, reason = classify_page(
        {"id": "topologie-bomber-strap"},
        "Product page",
        PageSignals(final_url="https://example.com", visible_text="Checking if the site connection is secure"),
    )

    assert status == MANUAL_CHECK
    assert "blocked" in reason


def test_classifies_lego_target_sizes_as_sold_out():
    status, reason = classify_page(
        {"id": "lego-brick-clog"},
        "Product page",
        PageSignals(
            final_url="https://lego.example",
            visible_text="M8 | W10 ($149.99) Sold out M9 | W11 ($149.99) Sold out M10 | W12 ($149.99) Sold out",
            buttons=[{"text": "Add to Bag", "enabled": True}],
        ),
    )

    assert status == SOLD_OUT
    assert "All target LEGO sizes" in reason


def test_classifies_lego_target_sizes_from_button_text():
    status, reason = classify_page(
        {"id": "lego-brick-clog"},
        "Product page",
        PageSignals(
            final_url="https://lego.example",
            visible_text="Brick Clog Select size Add to Bag",
            buttons=[
                {"text": "M8 | W10 ($149.99)Sold out", "enabled": True},
                {"text": "M9 | W11 ($149.99)Sold out", "enabled": True},
                {"text": "M10 | W12 ($149.99)Sold out", "enabled": True},
                {"text": "Add to Bag", "enabled": True},
            ],
        ),
    )

    assert status == SOLD_OUT
    assert "All target LEGO sizes" in reason
