"""Enrichment stage: attach a description + taxonomy to a normalized product.

The merge is deliberately **non-destructive**: re-running enrichment never wipes
choices the reviewer has already made. The description is always (re)generated;
suggested categories are unioned with the reviewer's; for properties the
reviewer's value wins per group. This keeps "AI suggests, human decides".
"""

from __future__ import annotations

from app.domain.models import NormalizedProduct
from app.services.llm import LLMProvider, get_provider
from app.services.llm.base import EnrichmentResult
from app.services.shop.base import ShopClient

_MAX_CATEGORIES = 3


def suggest(
    product: NormalizedProduct,
    shop: ShopClient,
    *,
    provider: LLMProvider | None = None,
    keywords: str = "",
) -> EnrichmentResult:
    provider = provider or get_provider()
    return provider.enrich_product(
        product,
        available_categories=shop.list_category_paths(),
        available_properties=shop.list_property_options(),
        keywords=keywords,
    )


def enrich(
    product: NormalizedProduct,
    shop: ShopClient,
    *,
    provider: LLMProvider | None = None,
    keywords: str = "",
) -> NormalizedProduct:
    result = suggest(product, shop, provider=provider, keywords=keywords)

    categories = list(product.categories)
    for cat in result.categories:
        if cat not in categories and len(categories) < _MAX_CATEGORIES:
            categories.append(cat)

    properties = {**result.properties, **product.properties}

    return product.model_copy(
        update={
            "description": result.description,
            "categories": categories,
            "properties": properties,
        }
    )
