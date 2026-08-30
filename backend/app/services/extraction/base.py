"""Document-extraction boundary.

A `DocumentExtractionProvider` turns a supplier document (a PDF order
confirmation, a delivery note, a phone photo of a paper order) into a list of
`RawSupplierProduct`.

In production this is one supplier-specific LLM prompt per supplier, sent with
the document to a hosted model, whose JSON reply is parsed. Here it is a
deterministic offline mock. The interface is identical; only the implementation
and the `SourceDocument.is_mock` flag differ.
"""

from __future__ import annotations

import abc

from app.domain.models import RawSupplierProduct

SUPPORTED_MEDIA_TYPES = {"application/pdf", "image/jpeg", "image/png"}


class DocumentExtractionError(RuntimeError):
    """Extraction failed for a reason worth showing the user."""


class UnsupportedMediaType(DocumentExtractionError):
    """The document is not a PDF or image."""


class DocumentNotRecognized(DocumentExtractionError):
    """The provider could not extract products from this document.

    Mirrors the production failure mode where the LLM returns nothing usable.
    """


class DocumentExtractionProvider(abc.ABC):
    name: str

    @abc.abstractmethod
    def extract(
        self, *, supplier_id: str, document: bytes, media_type: str
    ) -> list[RawSupplierProduct]:
        """Extract raw products from one supplier document.

        Raises `UnsupportedMediaType` for non-PDF/image input and
        `DocumentNotRecognized` when nothing usable can be extracted.
        """
