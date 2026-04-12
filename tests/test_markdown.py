from fashionbot.markdown import render_watchlist_markdown


def test_render_watchlist_markdown_groups_by_status():
    data = {
        "items": [
            {
                "id": "lego-brick-clog",
                "brand": "LEGO",
                "product": "Brick Clog",
                "variant": "M8 OR M9 OR M10",
                "price_target": None,
                "original_vendor_availability": "sold_out",
                "last_checked": "2026-04-12T10:00:00-04:00",
                "original_vendor_urls": [{"label": "Product page", "url": "https://lego.example"}],
                "notes": "All target sizes sold out.",
            }
        ]
    }

    markdown = render_watchlist_markdown(data)

    assert "## Sold out" in markdown
    assert "### LEGO - Brick Clog" in markdown
    assert "M8, M9, or M10 only" in markdown
