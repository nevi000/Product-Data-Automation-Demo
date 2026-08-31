from __future__ import annotations

from app.domain.models import (
    NormalizedProduct,
    PipelineResult,
    RawSupplierProduct,
    ReviewProduct,
    SourceDocument,
)
from app.domain.pricing import DEFAULT_PRICING, PricingPolicy
from app.services.completeness import build_checklist
from app.services.extraction.base import DocumentExtractionProvider
from app.services.normalization import normalize
from app.services.validation import validate
from app.suppliers.base import SupplierAdapter


#validate a product and build its checklist
def review(product: NormalizedProduct) -> ReviewProduct:
    return ReviewProduct(
        product=product,
        issues=validate(product),
        checklist=build_checklist(product),
    )

def _result(
    *,
    supplier_id: str,
    supplier_name: str,
    raw_products: list[RawSupplierProduct],
    pricing: PricingPolicy,
    source_reference: str | None = None,
    source_document: SourceDocument | None = None,
) -> PipelineResult:
    review_products = [
        review(normalize(raw, pricing=pricing)) for raw in raw_products
    ]
    return PipelineResult(
        supplier_id=supplier_id,
        supplier_name=supplier_name,
        source_reference=source_reference,
        source_document=source_document,
        raw_products=raw_products,
        review_products=review_products,
    )


def ingest_document(
    *,
    extractor: DocumentExtractionProvider,
    supplier_id: str,
    supplier_name: str,
    document: bytes,
    media_type: str,
    filename: str,
    pricing: PricingPolicy = DEFAULT_PRICING,
) -> PipelineResult:
    raw_products = extractor.extract(
        supplier_id=supplier_id, document=document, media_type=media_type
    )
    source_document = SourceDocument(
        filename=filename,
        media_type=media_type,
        extractor=type(extractor).__name__,
        is_mock=extractor.name == "mock",
        note=(
            "Production reads this with a supplier-specific LLM prompt; "
            "this demo uses a deterministic offline mock."
        ),
    )
    return _result(
        supplier_id=supplier_id,
        supplier_name=supplier_name,
        raw_products=raw_products,
        pricing=pricing,
        source_document=source_document,
    )

#Developer entry point
def ingest(
    adapter: SupplierAdapter,
    payload: bytes,
    *,
    source_reference: str | None = None,
    pricing: PricingPolicy = DEFAULT_PRICING,
) -> PipelineResult:
    return _result(
        supplier_id=adapter.id,
        supplier_name=adapter.name,
        raw_products=adapter.parse(payload),
        pricing=pricing,
        source_reference=source_reference,
    )
