from __future__ import annotations

import abc

from app.domain.models import RawSupplierProduct

SUPPORTED_MEDIA_TYPES = {"application/pdf", "image/jpeg", "image/png"}


class DocumentExtractionError(RuntimeError):
    """Extraction failed for a reason worth showing the user."""


class UnsupportedMediaType(DocumentExtractionError):
    """The document is not a PDF or image."""


class DocumentNotRecognized(DocumentExtractionError):
    """The provider could not extract products from this document."""


class DocumentExtractionProvider(abc.ABC):
    name: str

    @abc.abstractmethod
    def extract(
        self, *, supplier_id: str, document: bytes, media_type: str
    ) -> list[RawSupplierProduct]:
        """Raises UnsupportedMediaType or DocumentNotRecognized on bad input."""
