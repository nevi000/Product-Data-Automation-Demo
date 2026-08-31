import json

import pytest

from app.suppliers.alpinewear import AlpineWearAdapter
from app.suppliers.base import SupplierParseError

adapter = AlpineWearAdapter()


def test_parses_active_products_only(alpinewear_feed):
    products = adapter.parse(alpinewear_feed)
    skus = [p.source_reference for p in products]
    assert "AW-4470" not in skus          # status: discontinued
    assert skus == ["AW-4471", "AW-4472", "AW-2210", "AW-9001"]


def test_size_map_becomes_sizes_and_eans(alpinewear_feed):
    jacket = adapter.parse(alpinewear_feed)[0]
    assert jacket.sizes == ["S", "M", "L", "XL"]
    assert jacket.ean_by_size["M"] == "4012345000022"


def test_bare_size_list_supported(alpinewear_feed):
    base_layer = adapter.parse(alpinewear_feed)[2]
    assert base_layer.sizes == ["XS", "S", "M", "L", "XL"]
    assert base_layer.ean_by_size == {}


def test_price_string_with_currency_suffix(alpinewear_feed):
    jacket = adapter.parse(alpinewear_feed)[0]
    assert str(jacket.purchase_price) == "84.00 EUR"
    assert str(jacket.suggested_retail_price) == "199.00 EUR"


def test_sizeless_product_keeps_top_level_ean(alpinewear_feed):
    beanie = adapter.parse(alpinewear_feed)[3]
    assert beanie.sizes == []
    assert beanie.ean == "4012345099013"


def test_color_object_and_string_both_work(alpinewear_feed):
    products = adapter.parse(alpinewear_feed)
    assert products[0].color_name == "Forest Green"   # from {name, code}
    assert products[0].color_code == "GRN"
    assert products[2].color_name == "Charcoal"       # from plain string


def test_invalid_json_raises_parse_error():
    with pytest.raises(SupplierParseError):
        adapter.parse(b"{not json")


def test_wrong_shape_raises_parse_error():
    with pytest.raises(SupplierParseError):
        adapter.parse(json.dumps({"items": []}).encode())
