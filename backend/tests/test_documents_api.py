import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


def test_list_documents(client):
    body = client.get("/api/documents").json()
    assert {d["supplier_id"] for d in body} == {"alpinewear", "urbanthreads", "demoshoes"}
    aw = next(d for d in body if d["supplier_id"] == "alpinewear")
    assert aw["filename"] == "AlpineWear_OrderConfirmation.pdf"
    assert aw["media_type"] == "application/pdf"
    assert aw["kind"] == "Order confirmation"
    assert aw["product_count"] == 4


def test_download_document(client):
    r = client.get("/api/documents/alpinewear/file")
    assert r.status_code == 200
    assert r.headers["content-type"] == "application/pdf"
    assert r.content.startswith(b"%PDF")


def test_analyze_bundled_document(client):
    r = client.post("/api/documents/alpinewear/analyze")
    assert r.status_code == 200
    body = r.json()
    assert body["count"] == 4
    assert body["supplier_name"] == "AlpineWear"
    sd = body["source_document"]
    assert sd["filename"] == "AlpineWear_OrderConfirmation.pdf"
    assert sd["is_mock"] is True
    assert sd["extractor"] == "MockDocumentExtractor"
    # products go through the same normalize + review as the adapter path
    rp = body["review_products"][0]
    assert rp["product"]["product_number"] == "aw_4471_grn"
    assert "checklist" in rp and "fields_remaining" in rp


def test_analyze_unknown_supplier_404(client):
    assert client.post("/api/documents/nope/analyze").status_code == 404


def test_extract_uploaded_matching_document(client):
    doc = client.get("/api/documents/demoshoes/file").content
    r = client.post(
        "/api/documents/demoshoes/extract",
        files={"file": ("DemoShoes_Order.jpg", doc, "image/jpeg")},
    )
    assert r.status_code == 200
    assert r.json()["count"] == 2


def test_extract_uploaded_arbitrary_pdf_is_422(client):
    r = client.post(
        "/api/documents/alpinewear/extract",
        files={"file": ("mine.pdf", b"%PDF-1.4 not the bundled doc", "application/pdf")},
    )
    assert r.status_code == 422
    assert "bundled sample documents" in r.json()["detail"]


def test_extract_uploaded_non_document_is_415(client):
    r = client.post(
        "/api/documents/alpinewear/extract",
        files={"file": ("data.csv", b"a;b\n1;2", "text/csv")},
    )
    assert r.status_code == 415
