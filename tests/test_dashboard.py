from fashionbot.dashboard import render_dashboard_html


def test_render_dashboard_html_includes_status_counts_and_item_rows():
    data = {
        "items": [
            {
                "id": "topologie-bungee-wrist-strap",
                "brand": "Topologie",
                "product": "Bungee Wrist Strap",
                "variant": "Mint",
                "price_target": 45,
                "original_vendor_availability": "available",
                "original_price": "$45",
                "color_available": "Mint",
                "last_checked": "2026-04-12T17:09:22-04:00",
                "notes": "Enabled purchase button is visible.",
                "link_to_suggested_purchase": "https://topologie.example/product",
                "original_vendor_urls": [{"label": "Product page", "url": "https://topologie.example/product"}],
            },
            {
                "id": "lego-brick-clog",
                "brand": "LEGO",
                "product": "Brick Clog",
                "variant": "M8 OR M9 OR M10",
                "price_target": None,
                "original_vendor_availability": "sold_out",
                "last_checked": "2026-04-12T16:00:00-04:00",
                "notes": "All checked URLs are explicitly sold out.",
                "original_vendor_urls": [{"label": "Product page", "url": "https://lego.example/product"}],
            },
        ]
    }

    html = render_dashboard_html(data)

    assert "<title>Fashion Availability</title>" in html
    assert "Latest check: 2026-04-12 5:09 PM -0400" in html
    assert "Topologie - Bungee Wrist Strap" in html
    assert "LEGO - Brick Clog" in html
    assert "metric-available" in html
    assert 'href="https://topologie.example/product"' in html
