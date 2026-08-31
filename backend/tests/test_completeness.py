from decimal import Decimal

from app.domain.models import Money, NormalizedProduct, Variant
from app.services.completeness import build_checklist
from app.services.pipeline import review


def _product(**kw) -> NormalizedProduct:
    base = dict(
        supplier_id="x",
        product_number="art_1_grn",
        name="Field Jacket Green",
        variants=[Variant(size="M", active=True), Variant(size="L", active=True)],
        retail_price=Money(amount=Decimal("120")),
    )
    base.update(kw)
    return NormalizedProduct(**base)


def _by_key(product):
    return {c.key: c for c in build_checklist(product)}


def test_freshly_imported_product_needs_category_description_care():
    items = _by_key(_product())
    assert items["basics"].done and items["variants"].done
    assert not items["category"].done
    assert not items["description"].done
    assert not items["care"].done
    assert items["images"].required is False


def test_completed_product_is_exportable():
    p = _product(
        categories=["Home / Women / Outerwear / Insulated Jackets"],
        description="A warm, packable insulated jacket for cold-weather layering.",
        care_instructions="Machine wash cold",
    )
    r = review(p)
    assert r.fields_remaining == 0
    assert r.exportable is True


def test_fields_remaining_counts_only_required_items():
    r = review(_product(care_instructions="Wipe clean"))
    # category + description still missing
    assert r.fields_remaining == 2
    assert r.exportable is False


def test_sizeless_product_does_not_need_variants():
    p = _product(variants=[], ean="4012345099013")
    assert _by_key(p)["variants"].done is True


def test_product_with_inactive_only_variants_is_incomplete():
    p = _product(variants=[Variant(size="M", active=False)])
    assert _by_key(p)["variants"].done is False


def test_short_description_does_not_count_as_done():
    assert _by_key(_product(description="Nice."))["description"].done is False


def test_data_error_also_blocks_export():
    p = _product(
        name="  ",
        categories=["Home / Women / Knitwear"],
        description="A soft everyday knit in a relaxed fit.",
        care_instructions="Hand wash",
    )
    assert review(p).exportable is False  # blocked by name.missing
