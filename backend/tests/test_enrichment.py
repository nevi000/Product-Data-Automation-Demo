from decimal import Decimal

from app.domain.models import Money, NormalizedProduct, Variant
from app.services.enrichment import enrich, suggest
from app.services.shop.mock_adapter import MockShopAdapter

shop = MockShopAdapter()


def _product(**kw) -> NormalizedProduct:
    base = dict(
        supplier_id="alpinewear",
        product_number="aw_4471_grn",
        name="Ridgeline Insulated Jacket Forest Green",
        color="Forest Green",
        material="Recycled polyester",
        product_type="womens_outerwear",
        variants=[Variant(size="M")],
        retail_price=Money(amount=Decimal("199")),
    )
    base.update(kw)
    return NormalizedProduct(**base)


def test_suggest_picks_from_shop_taxonomy_only():
    result = suggest(_product(), shop)
    valid = set(shop.list_category_paths())
    assert all(c in valid for c in result.categories)
    assert result.description


def test_suggest_respects_product_gender():
    cats = suggest(_product(product_type="womens_outerwear"), shop).categories
    assert cats and all("/ Men /" not in c for c in cats)


def test_suggest_matches_colour_property():
    props = suggest(_product(), shop).properties
    assert props.get("Color") == "Forest Green"


def test_enrich_is_non_destructive():
    p = _product(
        categories=["Home / Women / Knitwear"],
        properties={"Fit": "Relaxed"},
    )
    out = enrich(p, shop)
    # reviewer's manual picks are kept
    assert "Home / Women / Knitwear" in out.categories
    assert out.properties["Fit"] == "Relaxed"
    # and the description is (re)generated
    assert out.description


def test_enrich_caps_categories():
    out = enrich(_product(categories=["A", "B", "C"]), shop)
    assert out.categories == ["A", "B", "C"]  # already at cap, nothing added


def test_keyword_hint_beanie_maps_to_headwear():
    beanie = _product(name="Summit Wool Beanie Rust", product_type="accessory")
    assert suggest(beanie, shop).categories == ["Home / Accessories / Headwear"]
