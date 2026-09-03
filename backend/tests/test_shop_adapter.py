from decimal import Decimal

import pytest

from app.domain.models import Money, NormalizedProduct, Variant
from app.services.shop.base import ShopWriteError
from app.services.shop.mock_adapter import MockShopAdapter


def _product(number="art_1_grn", **kw) -> NormalizedProduct:
    base = dict(
        supplier_id="x",
        product_number=number,
        name="Field Jacket Green",
        material="Cotton",
        care_instructions="Machine wash cold",
        product_type="mens_outerwear",
        size_chart="sc_mens_apparel",
        variants=[Variant(size="S"), Variant(size="M")],
        retail_price=Money(amount=Decimal("120")),
        purchase_price=Money(amount=Decimal("48")),
        categories=["Home / Men / Outerwear / Shell Jackets"],
        properties={"Color": "Green"},
    )
    base.update(kw)
    return NormalizedProduct(**base)


def test_create_product_returns_variant_and_category_counts():
    shop = MockShopAdapter()
    created = shop.create_product(_product())
    assert created.variant_count == 2
    assert created.category_paths == ["Home / Men / Outerwear / Shell Jackets"]
    assert created.url.startswith("https://demo-shop.local/admin/product/")


def test_product_without_size_variants_has_zero_variant_count():
    shop = MockShopAdapter()
    created = shop.create_product(_product(variants=[]))
    assert created.variant_count == 0


def test_payload_carries_reviewer_classification():
    shop = MockShopAdapter()
    created = shop.create_product(_product())
    payload = created.payload
    assert payload["productType"] == "mens_outerwear"
    assert payload["sizeChartId"] == "sc_mens_apparel"
    assert payload["manufacturer"] is None
    groups = {p["group"] for p in payload["properties"]}
    assert {"Color", "Material", "Care"} <= groups
    assert created.property_count == len(payload["properties"])


def test_product_without_category_rejected():
    shop = MockShopAdapter()
    with pytest.raises(ShopWriteError):
        shop.create_product(_product(categories=[]))


def test_upsert_property_option_is_idempotent():
    shop = MockShopAdapter()
    first = shop.upsert_property_option("Size", "42")
    second = shop.upsert_property_option("Size", "42")
    assert first == second


def test_duplicate_product_number_rejected():
    shop = MockShopAdapter()
    shop.create_product(_product())
    with pytest.raises(ShopWriteError):
        shop.create_product(_product())


def test_product_without_price_rejected():
    shop = MockShopAdapter()
    with pytest.raises(ShopWriteError):
        shop.create_product(_product(retail_price=None))


def test_created_product_is_retrievable():
    shop = MockShopAdapter()
    shop.create_product(_product(number="abc_1"))
    assert shop.get_product("abc_1") is not None
    assert shop.get_product("missing") is None
