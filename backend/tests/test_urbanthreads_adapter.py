import pytest

from app.suppliers.base import SupplierParseError
from app.suppliers.urbanthreads import UrbanThreadsAdapter

adapter = UrbanThreadsAdapter()


def test_rows_grouped_into_products(urbanthreads_export):
    products = adapter.parse(urbanthreads_export)
    # UT-1001 in two colours, UT-2044, UT-3300 => 4 products
    assert len(products) == 4
    refs = sorted({p.source_reference for p in products})
    assert refs == ["UT-1001", "UT-2044", "UT-3300"]


def test_sizes_accumulate_per_group(urbanthreads_export):
    black_tee = next(
        p for p in adapter.parse(urbanthreads_export)
        if p.source_reference == "UT-1001" and p.color_name == "Washed Black"
    )
    assert black_tee.sizes == ["S", "M", "L", "XL"]
    assert black_tee.ean_by_size["M"] == "4056789000029"


def test_zero_quantity_rows_dropped(urbanthreads_export):
    bone_tee = next(
        p for p in adapter.parse(urbanthreads_export)
        if p.source_reference == "UT-1001" and p.color_name == "Bone"
    )
    assert "S" not in bone_tee.sizes          # the only Bone/S row had quantity 0
    assert bone_tee.sizes == ["M", "L"]


def test_shipping_pseudo_line_skipped(urbanthreads_export):
    assert all(
        p.source_reference != "SHIPPING" for p in adapter.parse(urbanthreads_export)
    )


def test_european_decimal_comma_prices(urbanthreads_export):
    cargo = next(
        p for p in adapter.parse(urbanthreads_export)
        if p.source_reference == "UT-2044"
    )
    assert str(cargo.purchase_price) == "28.00 EUR"
    assert str(cargo.suggested_retail_price) == "79.00 EUR"


def test_missing_ean_cell_is_tolerated(urbanthreads_export):
    cargo = next(
        p for p in adapter.parse(urbanthreads_export)
        if p.source_reference == "UT-2044"
    )
    assert "XL" in cargo.sizes
    assert "XL" not in cargo.ean_by_size


def test_missing_required_columns_raises():
    with pytest.raises(SupplierParseError):
        adapter.parse(b"foo;bar\n1;2\n")
