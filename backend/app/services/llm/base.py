from __future__ import annotations

import abc

from pydantic import BaseModel, Field

from app.domain.models import NormalizedProduct


class LLMQuotaError(RuntimeError):
    """Provider rate-limit / quota exhausted. Mapped to HTTP 402 at the edge."""

class EnrichmentResult(BaseModel):
    description: str
    categories: list[str] = Field(default_factory=list)
    properties: dict[str, str] = Field(default_factory=dict)

class LLMProvider(abc.ABC):
    name: str

    @abc.abstractmethod
    def enrich_product(
        self,
        product: NormalizedProduct,
        *,
        available_categories: list[str],
        available_properties: dict[str, list[str]],
        keywords: str = "",
    ) -> EnrichmentResult:
        """Write a description and pick categories/properties for one product."""