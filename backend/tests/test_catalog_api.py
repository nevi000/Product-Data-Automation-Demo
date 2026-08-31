import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


def test_categories_are_paths(client):
    cats = client.get("/api/catalog/categories").json()
    assert all(" / " in c for c in cats)
    assert any(c.startswith("Home / Footwear") for c in cats)


def test_property_groups(client):
    props = client.get("/api/catalog/properties").json()
    assert set(props) == {"Color", "Fit", "Sleeve length", "Product style", "Neckline"}
    assert "Forest Green" in props["Color"]


def test_product_types_map_to_size_presets(client):
    types = client.get("/api/catalog/product-types").json()
    keys = {t["key"] for t in types}
    assert {"womens_footwear", "accessory", "homeware"} <= keys
    homeware = next(t for t in types if t["key"] == "homeware")
    assert homeware["size_preset"] is None


def test_size_charts(client):
    charts = client.get("/api/catalog/size-charts").json()
    assert {"id", "name"} <= set(charts[0])


def test_sizes_for_product_type(client):
    r = client.get("/api/catalog/product-types/mens_footwear/sizes")
    assert r.status_code == 200
    assert r.json()["sizes"] == ["39", "40", "41", "42", "43", "44", "45", "46", "47"]


def test_sizes_for_homeware_is_empty(client):
    assert client.get("/api/catalog/product-types/homeware/sizes").json()["sizes"] == []


def test_unknown_product_type_404(client):
    assert client.get("/api/catalog/product-types/nope/sizes").status_code == 404
