import pytest

from app.services.extraction import (
    DEMO_DOCUMENTS,
    DemoDocument,
    DocumentNotRecognized,
    MockDocumentExtractor,
    UnsupportedMediaType,
    get_extractor,
)
from app.services.extraction.documents import DemoLine
from app.services.normalization import normalize

extractor = MockDocumentExtractor()


def test_get_extractor_returns_the_mock():
    assert get_extractor("mock").name == "mock"
    with pytest.raises(ValueError):
        get_extractor("does-not-exist")


def test_bundled_documents_exist_and_match_fixture_counts():
    for demo in DEMO_DOCUMENTS.values():
        assert demo.path.exists(), f"{demo.filename} not generated"
        assert demo.product_count == len(demo.lines)


def test_extracts_the_documented_products(alpinewear_document):
    raw = extractor.extract(
        supplier_id="alpinewear",
        document=alpinewear_document,
        media_type="application/pdf",
    )
    assert [r.source_reference for r in raw] == ["AW-4471", "AW-4472", "AW-2210", "AW-9001"]
    jacket = raw[0]
    assert jacket.model_name == "Ridgeline Insulated Jacket"
    assert jacket.sizes == ["S", "M", "L", "XL"]
    assert jacket.ean_by_size["M"] == "4012345000022"
    assert str(jacket.purchase_price) == "84.00 EUR"
    assert jacket.raw["document"] == "AlpineWear_OrderConfirmation.pdf"
    assert jacket.raw["extracted_by"] == "MockDocumentExtractor"


def test_extracted_products_normalize_cleanly(alpinewear_document):
    raw = extractor.extract(
        supplier_id="alpinewear",
        document=alpinewear_document,
        media_type="application/pdf",
    )
    products = [normalize(r) for r in raw]
    assert products[0].product_number == "aw_4471_grn"
    assert products[0].name == "Ridgeline Insulated Jacket Forest Green"
    assert products[0].care_instructions  # carried from the document
    assert [v.size for v in products[0].variants] == ["S", "M", "L", "XL"]


def test_image_document_is_supported(demoshoes_document):
    raw = extractor.extract(
        supplier_id="demoshoes",
        document=demoshoes_document,
        media_type="image/jpeg",
    )
    assert [r.source_reference for r in raw] == ["DS-TRK-01", "DS-CHL-07"]


def test_non_pdf_image_is_rejected(alpinewear_document):
    with pytest.raises(UnsupportedMediaType):
        extractor.extract(
            supplier_id="alpinewear", document=alpinewear_document, media_type="text/csv"
        )


def test_unknown_document_is_not_recognized():
    with pytest.raises(DocumentNotRecognized):
        extractor.extract(
            supplier_id="alpinewear",
            document=b"%PDF-1.4 some other order",
            media_type="application/pdf",
        )


def test_unknown_supplier_is_not_recognized(alpinewear_document):
    with pytest.raises(DocumentNotRecognized):
        extractor.extract(
            supplier_id="nope", document=alpinewear_document, media_type="application/pdf"
        )


def test_injected_document_supplies_its_own_metadata(alpinewear_document):
    doc = DemoDocument(
        supplier_id="acme",
        supplier_name="Acme Supply Co",
        filename="AlpineWear_OrderConfirmation.pdf",
        media_type="application/pdf",
        kind="Order confirmation",
        doc_number="ACME-1",
        doc_date="2026-01-01",
        lines=[DemoLine(position=1, source_reference="ACME-1", model_name="Widget")],
    )
    ext = MockDocumentExtractor(documents={"acme": doc})

    raw = ext.extract(
        supplier_id="acme", document=alpinewear_document, media_type="application/pdf"
    )
    assert len(raw) == 1
    assert raw[0].supplier_id == "acme"
    assert raw[0].manufacturer == "Acme Supply Co"
    assert raw[0].raw["document"] == "AlpineWear_OrderConfirmation.pdf"
    assert "acme" not in DEMO_DOCUMENTS
