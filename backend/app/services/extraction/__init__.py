from app.services.extraction.base import (
    DocumentExtractionError,
    DocumentExtractionProvider,
    DocumentNotRecognized,
    UnsupportedMediaType,
)
from app.services.extraction.documents import DEMO_DOCUMENTS, DemoDocument
from app.services.extraction.mock import MockDocumentExtractor

__all__ = [
    "DEMO_DOCUMENTS",
    "DemoDocument",
    "DocumentExtractionError",
    "DocumentExtractionProvider",
    "DocumentNotRecognized",
    "MockDocumentExtractor",
    "UnsupportedMediaType",
    "get_extractor",
]

_PROVIDERS = {"mock": MockDocumentExtractor}

def get_extractor(name: str = "mock") -> DocumentExtractionProvider:
    try:
        return _PROVIDERS[name]()
    except KeyError:
        raise ValueError(f"unknown document extractor: {name!r}") from None
