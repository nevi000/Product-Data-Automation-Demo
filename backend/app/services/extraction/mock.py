"""Deterministic, offline mock document extractor.

Stands in for the production step "send the PDF + a supplier-specific prompt to a
hosted LLM, parse the JSON reply". Here the reply is fixed per bundled document
(`documents.py`). No network, no API key, fully reproducible.

It still models the real boundary:

* it only accepts PDF / image media types,
* it only recognizes the bundled fictional documents (an uploaded arbitrary PDF
  raises `DocumentNotRecognized`, the same way a real prompt would return
  nothing usable for an unknown layout),
* it returns loosely-typed `RawSupplierProduct`s — normalization and validation
  happen in later stages, exactly as in production.
"""

from __future__ import annotations

import hashlib

from app.domain.models import RawSupplierProduct
from app.services.extraction.base import (
    SUPPORTED_MEDIA_TYPES,
    DocumentExtractionProvider,
    DocumentNotRecognized,
    UnsupportedMediaType,
)
from app.services.extraction.documents import DEMO_DOCUMENTS, DemoDocument, DemoLine


def _to_raw(supplier_id: str, filename: str, line: DemoLine) -> RawSupplierProduct:
    return RawSupplierProduct(
        supplier_id=supplier_id,
        source_reference=line.source_reference,
        model_name=line.model_name,
        color_name=line.color_name,
        color_code=line.color_code,
        manufacturer=DEMO_DOCUMENTS[supplier_id].supplier_name,
        material=line.material,
        care_instructions=line.care_instructions,
        sizes=list(line.sizes),
        ean_by_size=dict(line.ean_by_size),
        ean=line.ean,
        purchase_price=line.purchase_price,
        suggested_retail_price=line.suggested_retail_price,
        raw={
            "document": filename,
            "position": line.position,
            "extracted_by": "MockDocumentExtractor",
        },
    )


class MockDocumentExtractor(DocumentExtractionProvider):
    name = "mock"

    def __init__(self, documents: dict[str, DemoDocument] | None = None) -> None:
        self._documents = documents or DEMO_DOCUMENTS

    def extract(
        self, *, supplier_id: str, document: bytes, media_type: str
    ) -> list[RawSupplierProduct]:
        if media_type not in SUPPORTED_MEDIA_TYPES:
            raise UnsupportedMediaType(
                f"{media_type!r} is not a PDF or image — supply a PDF or a photo."
            )

        demo = self._documents.get(supplier_id)
        if demo is None or not self._matches_bundled(demo, document):
            raise DocumentNotRecognized(
                "This demo extractor only recognizes the bundled sample documents. "
                "To try your own data, use the structured-file adapters under "
                '"Developer tools".'
            )

        return [_to_raw(supplier_id, demo.filename, line) for line in demo.lines]

    @staticmethod
    def _matches_bundled(demo: DemoDocument, document: bytes) -> bool:
        try:
            expected = demo.path.read_bytes()
        except OSError:
            return False
        return hashlib.sha256(document).digest() == hashlib.sha256(expected).digest()
