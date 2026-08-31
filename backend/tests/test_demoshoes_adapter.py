import pytest

from app.suppliers.base import SupplierParseError
from app.suppliers.demoshoes import DemoShoesAdapter

adapter = DemoShoesAdapter()


def test_parses_three_products(demoshoes_catalog):
    products = adapter.parse(demoshoes_catalog)
    assert [p.source_reference for p in products] == ["DS-TRK-01", "DS-TRK-02", "DS-CHL-07"]


def test_sold_out_sizes_are_skipped(demoshoes_catalog):
    trk01 = adapter.parse(demoshoes_catalog)[0]
    assert "43" not in trk01.sizes            # <td class="sold-out">43</td>
    assert trk01.sizes == ["39", "40", "41", "42", "44", "45"]


def test_data_ean_attribute_is_read(demoshoes_catalog):
    trk01 = adapter.parse(demoshoes_catalog)[0]
    assert trk01.ean_by_size["41"] == "4098765000032"
    assert "43" not in trk01.ean_by_size


def test_price_with_euro_sign_and_comma(demoshoes_catalog):
    trk01 = adapter.parse(demoshoes_catalog)[0]
    assert str(trk01.purchase_price) == "59.90 EUR"


def test_colour_lowercased(demoshoes_catalog):
    boot = adapter.parse(demoshoes_catalog)[2]
    assert boot.color_name == "dark brown"


def test_non_catalogue_html_raises():
    with pytest.raises(SupplierParseError):
        adapter.parse(b"<html><body><p>hello</p></body></html>")
