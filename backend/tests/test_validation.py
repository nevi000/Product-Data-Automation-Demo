from decimal import Decimal

from app.domain.models import Money, NormalizedProduct, Severity, Variant
from app.services.validation import validate


def _product(**kw) -> NormalizedProduct:
    base = dict(
        supplier_id="x",
        product_number="art_1_grn",
        name="Field Jacket Green",
        variants=[Variant(size="M", ean="4012345000022")],
        retail_price=Money(amount=Decimal("120")),
        purchase_price=Money(amount=Decimal("48")),
    )
    base.update(kw)
    return NormalizedProduct(**base)


def _codes(product):
    return {i.code for i in validate(product)}


def test_well_formed_data_has_no_issues():
    # validation is about data correctness, not completeness — an imported
    # product with no category / description / care is still valid data.
    assert validate(_product()) == []


def test_missing_name_is_blocking_error():
    issues = validate(_product(name=" "))
    assert any(i.code == "name.missing" and i.severity is Severity.ERROR for i in issues)


def test_missing_price_is_blocking_error():
    assert "price.missing" in _codes(_product(retail_price=None, purchase_price=None))


def test_thin_margin_is_warning_not_error():
    issues = validate(_product(retail_price=Money(amount=Decimal("40"))))
    margin = next(i for i in issues if i.code == "price.margin")
    assert margin.severity is Severity.WARNING
    assert margin.blocking is False


def test_duplicate_size_is_blocking():
    p = _product(variants=[Variant(size="M"), Variant(size="M")])
    assert "variants.duplicate_size" in _codes(p)


def test_implausible_ean_is_warning():
    p = _product(variants=[Variant(size="M", ean="123")])
    issue = next(i for i in validate(p) if i.code == "ean.format")
    assert issue.severity is Severity.WARNING


def test_plausible_ean_passes():
    assert "ean.format" not in _codes(_product(variants=[Variant(size="M", ean="4012345000022")]))
