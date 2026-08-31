from decimal import Decimal

from app.domain.models import Money, RawSupplierProduct
from app.domain.pricing import PricingPolicy
from app.services.normalization import normalize


def _raw(**kw) -> RawSupplierProduct:
    base = dict(supplier_id="x", source_reference="ART-1", model_name="Field Jacket")
    base.update(kw)
    return RawSupplierProduct(**base)


def test_product_number_uses_reference_and_colour_code():
    p = normalize(_raw(color_code="GRN", color_name="Forest Green"))
    assert p.product_number == "art_1_grn"


def test_product_number_falls_back_to_colour_name():
    p = normalize(_raw(color_name="Forest Green", color_code=None))
    assert p.product_number == "art_1_forest_green"


def test_display_name_appends_colour_once():
    assert normalize(_raw(color_name="Green")).name == "Field Jacket Green"
    # colour already in the model name -> not duplicated
    dup = normalize(_raw(model_name="Green Field Jacket", color_name="Green"))
    assert dup.name == "Green Field Jacket"


def test_variants_carry_per_size_ean():
    p = normalize(_raw(sizes=["S", "M"], ean_by_size={"M": "4012345000022"}))
    assert [(v.size, v.ean) for v in p.variants] == [("S", None), ("M", "4012345000022")]


def test_duplicate_sizes_are_collapsed():
    p = normalize(_raw(sizes=["M", "M", "L"]))
    assert [v.size for v in p.variants] == ["M", "L"]


def test_retail_price_derived_when_supplier_gives_none():
    policy = PricingPolicy(landed_cost_factor=Decimal("1.1"), retail_multiplier=Decimal("2"))
    p = normalize(_raw(purchase_price=Money(amount=Decimal("50"))), pricing=policy)
    assert p.retail_price == Money(amount=Decimal("110"))


def test_supplier_retail_price_wins_over_policy():
    p = normalize(_raw(
        purchase_price=Money(amount=Decimal("50")),
        suggested_retail_price=Money(amount=Decimal("129")),
    ))
    assert p.retail_price == Money(amount=Decimal("129"))
