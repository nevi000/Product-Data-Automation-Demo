from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from pathlib import Path

from app.config import settings
from app.domain.models import Money

DOCUMENTS_DIR = settings.demo_data_dir / "documents"

def _eur(amount: str) -> Money:
    return Money(amount=Decimal(amount), currency="EUR")

@dataclass
class DemoLine:
    #one order line, as a supplier-specific LLM would extract it
    position: int
    source_reference: str | None
    model_name: str
    color_name: str | None = None
    color_code: str | None = None
    material: str | None = None
    care_instructions: str | None = None
    sizes: list[str] = field(default_factory=list)
    ean_by_size: dict[str, str] = field(default_factory=dict)
    ean: str | None = None
    purchase_price: Money | None = None
    suggested_retail_price: Money | None = None

@dataclass
class DemoDocument:
    supplier_id: str
    supplier_name: str
    filename: str
    media_type: str
    kind: str
    doc_number: str
    doc_date: str
    lines: list[DemoLine]

    @property
    def path(self) -> Path:
        return DOCUMENTS_DIR / self.filename

    @property
    def product_count(self) -> int:
        return len(self.lines)

#invented demo data for the mock document extractor
DEMO_DOCUMENTS: dict[str, DemoDocument] = {
    "alpinewear": DemoDocument(
        supplier_id="alpinewear",
        supplier_name="AlpineWear",
        filename="AlpineWear_OrderConfirmation.pdf",
        media_type="application/pdf",
        kind="Order confirmation",
        doc_number="AW-OC-20261-4471",
        doc_date="2026-02-03",
        lines=[
            DemoLine(
                position=10,
                source_reference="AW-4471",
                model_name="Ridgeline Insulated Jacket",
                color_name="Forest Green",
                color_code="GRN",
                material="100% recycled polyester, PrimaLoft insulation",
                care_instructions="Machine wash cold, do not tumble dry, do not iron",
                sizes=["S", "M", "L", "XL"],
                ean_by_size={
                    "S": "4012345000015",
                    "M": "4012345000022",
                    "L": "4012345000039",
                    "XL": "4012345000046",
                },
                purchase_price=_eur("84.00"),
                suggested_retail_price=_eur("199.00"),
            ),
            DemoLine(
                position=20,
                source_reference="AW-4472",
                model_name="Ridgeline Insulated Jacket",
                color_name="Slate Grey",
                color_code="GRY",
                material="100% recycled polyester, PrimaLoft insulation",
                care_instructions="Machine wash cold, do not tumble dry, do not iron",
                sizes=["S", "M", "L"],
                ean_by_size={
                    "S": "4012345000053",
                    "M": "4012345000060",
                    "L": "4012345000077",
                },
                purchase_price=_eur("84.00"),
                suggested_retail_price=_eur("199.00"),
            ),
            DemoLine(
                position=30,
                source_reference="AW-2210",
                model_name="Merino Base Layer Crew",
                color_name="Charcoal",
                color_code="CHR",
                material="87% merino wool, 13% nylon",
                care_instructions="Machine wash warm (max 40C), do not bleach, dry flat",
                sizes=["XS", "S", "M", "L", "XL"],
                purchase_price=_eur("39.50"),
            ),
            DemoLine(
                position=40,
                source_reference="AW-9001",
                model_name="Summit Wool Beanie",
                color_name="Rust",
                material="100% lambswool",
                ean="4012345099013",
                purchase_price=_eur("12.90"),
                suggested_retail_price=_eur("34.90"),
            ),
        ],
    ),
    "urbanthreads": DemoDocument(
        supplier_id="urbanthreads",
        supplier_name="UrbanThreads",
        filename="UrbanThreads_DeliveryNote.pdf",
        media_type="application/pdf",
        kind="Delivery note",
        doc_number="UT-DN-0091",
        doc_date="2026-02-05",
        lines=[
            DemoLine(
                position=1,
                source_reference="UT-1001",
                model_name="Boxy Logo Tee",
                color_name="Washed Black",
                color_code="001",
                material="100% organic cotton",
                care_instructions="Machine wash cold, tumble dry low",
                sizes=["S", "M", "L", "XL"],
                ean_by_size={
                    "S": "4056789000012",
                    "M": "4056789000029",
                    "L": "4056789000036",
                    "XL": "4056789000043",
                },
                purchase_price=_eur("9.50"),
                suggested_retail_price=_eur("29.90"),
            ),
            DemoLine(
                position=2,
                source_reference="UT-2044",
                model_name="Wide Leg Cargo Pant",
                color_name="Olive",
                color_code="050",
                material="68% cotton, 32% nylon",
                care_instructions="Machine wash cold, hang dry",
                sizes=["M", "L", "XL"],
                ean_by_size={"M": "4056789020045", "L": "4056789020052"},
                purchase_price=_eur("28.00"),
                suggested_retail_price=_eur("79.00"),
            ),
            DemoLine(
                position=3,
                source_reference="UT-3300",
                model_name="Half-Zip Fleece",
                color_name="Washed Black",
                color_code="001",
                material="100% polyester fleece",
                sizes=["S", "M", "L"],
                ean_by_size={
                    "S": "4056789033007",
                    "M": "4056789033014",
                    "L": "4056789033021",
                },
                purchase_price=_eur("22.00"),
            ),
        ],
    ),
    "demoshoes": DemoDocument(
        supplier_id="demoshoes",
        supplier_name="DemoShoes",
        filename="DemoShoes_Order.jpg",
        media_type="image/jpeg",
        kind="Order",
        doc_number="DS-2026-0148",
        doc_date="2026-01-28",
        lines=[
            DemoLine(
                position=1,
                source_reference="DS-TRK-01",
                model_name="Trail Runner Low",
                color_name="Graphite",
                sizes=["40", "41", "42", "44", "45"],
                ean_by_size={
                    "40": "4098765000025",
                    "41": "4098765000032",
                    "42": "4098765000049",
                    "44": "4098765000063",
                    "45": "4098765000070",
                },
                purchase_price=_eur("59.90"),
            ),
            DemoLine(
                position=2,
                source_reference="DS-CHL-07",
                model_name="Chelsea Boot",
                color_name="Dark Brown",
                sizes=["41", "42", "43", "44"],
                ean_by_size={
                    "41": "4098765070093",
                    "42": "4098765070109",
                    "43": "4098765070116",
                    "44": "4098765070123",
                },
                purchase_price=_eur("89.00"),
            ),
        ],
    ),
}