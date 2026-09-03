import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


def test_health(client):
    assert client.get("/health").json() == {"status": "ok"}


def test_list_suppliers(client):
    body = client.get("/api/suppliers").json()
    assert {s["id"] for s in body} == {"alpinewear", "urbanthreads", "demoshoes"}
    assert {s["input_format"] for s in body} == {"json", "csv", "html"}


def test_ingest_returns_review_products(client, alpinewear_feed):
    r = client.post(
        "/api/suppliers/alpinewear/ingest",
        files={"file": ("feed.json", alpinewear_feed, "application/json")},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["count"] == 4
    assert body["supplier_name"] == "AlpineWear"
    assert all("exportable" in rp for rp in body["review_products"])
    assert all("checklist" in rp and "fields_remaining" in rp for rp in body["review_products"])
    # imported jackets carry material + care; only category + description remain
    jacket = body["review_products"][0]
    assert jacket["fields_remaining"] == 2


def test_ingest_unknown_supplier_404(client, alpinewear_feed):
    r = client.post(
        "/api/suppliers/nope/ingest",
        files={"file": ("f.json", alpinewear_feed, "application/json")},
    )
    assert r.status_code == 404


def test_ingest_unparseable_document_422(client):
    r = client.post(
        "/api/suppliers/alpinewear/ingest",
        files={"file": ("f.json", b"{bad", "application/json")},
    )
    assert r.status_code == 422


def test_full_flow_ingest_enrich_complete_export(client, demoshoes_catalog):
    ingest = client.post(
        "/api/suppliers/demoshoes/ingest",
        files={"file": ("c.html", demoshoes_catalog, "text/html")},
    ).json()
    product = ingest["review_products"][0]["product"]

    # enrich fills description + suggests category
    enriched = client.post(
        "/api/products/enrich", json={"product": product, "keywords": "trail"}
    ).json()
    assert enriched["description"] and enriched["categories"]

    # still not exportable — the footwer feed has no care instructions
    review = client.post("/api/products/review", json=enriched).json()
    assert review["exportable"] is False
    assert "care" in [c["key"] for c in review["checklist"] if not c["done"]]

    blocked = client.post("/api/products/export", json=enriched)
    assert blocked.status_code == 422
    assert "care" in blocked.json()["detail"]["incomplete"]

    # reviewer completes the last field
    enriched["care_instructions"] = "Wipe with a damp cloth"
    exported = client.post("/api/products/export", json=enriched)
    assert exported.status_code == 200
    assert exported.json()["variant_count"] == len(product["variants"])


def test_image_job_accepts_a_png(client):
    r = client.post(
        "/api/products/images",
        files={"file": ("photo.png", b"\x89PNG\r\n\x1a\n" + b"0" * 32, "image/png")},
        data={"kind": "packshot"},
    )
    assert r.status_code == 200
    assert r.json()["status"] in {"processing", "completed"}


def test_image_job_rejects_unsupported_type(client):
    r = client.post(
        "/api/products/images",
        files={"file": ("photo.gif", b"GIF89a", "image/gif")},
        data={"kind": "packshot"},
    )
    assert r.status_code == 415


def test_image_job_rejects_oversized_upload(client):
    big = b"0" * (5 * 1024 * 1024 + 1)
    r = client.post(
        "/api/products/images",
        files={"file": ("photo.png", big, "image/png")},
        data={"kind": "packshot"},
    )
    assert r.status_code == 413


def test_export_blocked_by_data_error(client):
    product = {
        "supplier_id": "x",
        "product_number": "art_1",
        "name": "  ",
        "variants": [],
        "retail_price": None,
    }
    r = client.post("/api/products/export", json=product)
    assert r.status_code == 422
    assert r.json()["detail"]["errors"]  # genuine data errors listed
