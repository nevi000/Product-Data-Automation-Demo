"""Document extraction — the first stage of the pipeline.

Production: a supplier PDF / photo goes through a supplier-specific prompt on a
hosted LLM and comes back as structured raw products.

Public demo: bundled fictional PDF / image -> MockDocumentExtractor
(deterministic, offline, no API call) -> the same structured raw products.

Both sit behind one DocumentExtractionProvider interface so nothing downstream
knows which one ran.
"""

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
    """Return a document-extraction provider by name.

    Only the deterministic ``mock`` provider ships in this repo, so the demo runs
    with no API keys and no network. A real provider (a supplier-prompt library
    over a hosted LLM) is a drop-in: implement `DocumentExtractionProvider` and
    register it here.
    """
    try:
        return _PROVIDERS[name]()
    except KeyError:
        raise ValueError(f"unknown document extractor: {name!r}") from None
