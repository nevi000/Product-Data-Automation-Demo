from pathlib import Path

import pytest

DEMO_DATA = Path(__file__).resolve().parents[2] / "demo_data"
DOCUMENTS = DEMO_DATA / "documents"


@pytest.fixture
def demo_data() -> Path:
    return DEMO_DATA


@pytest.fixture
def alpinewear_feed() -> bytes:
    return (DEMO_DATA / "alpinewear_feed.json").read_bytes()


@pytest.fixture
def urbanthreads_export() -> bytes:
    return (DEMO_DATA / "urbanthreads_export.csv").read_bytes()


@pytest.fixture
def demoshoes_catalog() -> bytes:
    return (DEMO_DATA / "demoshoes_catalog.html").read_bytes()


@pytest.fixture
def alpinewear_document() -> bytes:
    return (DOCUMENTS / "AlpineWear_OrderConfirmation.pdf").read_bytes()


@pytest.fixture
def demoshoes_document() -> bytes:
    return (DOCUMENTS / "DemoShoes_Order.jpg").read_bytes()
