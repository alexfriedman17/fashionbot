from fashionbot.storage import load_watchlist, save_watchlist


def test_load_and_save_watchlist(tmp_path):
    path = tmp_path / "watchlist.json"
    data = {
        "version": 1,
        "items": [
            {
                "id": "item-1",
                "brand": "Brand",
                "product": "Product",
                "original_vendor_urls": [{"label": "Product page", "url": "https://example.com"}],
            }
        ],
    }

    save_watchlist(data, path)
    loaded = load_watchlist(path)

    assert loaded["items"][0]["id"] == "item-1"
