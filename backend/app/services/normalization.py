"""Normalization: RawSupplierProduct -> NormalizedProduct.

This is where the supplier-specific mess is turned into the one canonical shape:

* build a stable, shop-facing product number,
* fold model + colour into a display name (without duplicating the colour),
* attach per-size EANs to variants,
* apply the pricing policy when the supplier gave no retail price.

It is intentionally supplier-agnostic — it only sees `RawSupplierProduct`.
"""

from __future__ import annotations

from app.domain.models import (
    ManufacturerRef,
    NormalizedProduct,
    RawSupplierProduct,
    Variant,
)
from app.domain.pricing import DEFAULT_PRICING, PricingPolicy
from app.utils.text import slugify, titleize


def _product_number(raw: RawSupplierProduct) -> str:
    base = raw.source_reference or raw.model_name or "item"
    parts = [slugify(base)]
    if raw.color_code:
        parts.append(slugify(raw.color_code))
    elif raw.color_name:
        parts.append(slugify(raw.color_name))
    return "_".join(p for p in parts if p)


def _display_name(raw: RawSupplierProduct) -> str:
    model = titleize(raw.model_name or raw.source_reference or "Product")
    color = (raw.color_name or "").strip()
    if not color or color.lower() in model.lower():
        return model
    return f"{model} {titleize(color)}"


def normalize(
    raw: RawSupplierProduct,
    *,
    pricing: PricingPolicy = DEFAULT_PRICING,
) -> NormalizedProduct:
    variants = [
        Variant(size=size, ean=raw.ean_by_size.get(size), active=True)
        for size in _dedupe(raw.sizes)
    ]

    retail = raw.suggested_retail_price or pricing.suggest_retail(raw.purchase_price)

    manufacturer = None
    if raw.manufacturer:
        manufacturer = ManufacturerRef(name=titleize(raw.manufacturer))

    return NormalizedProduct(
        supplier_id=raw.supplier_id,
        product_number=_product_number(raw),
        source_reference=raw.source_reference,
        name=_display_name(raw),
        collection=raw.collection,
        color=raw.color_name,
        manufacturer=manufacturer,
        material=raw.material,
        care_instructions=raw.care_instructions,
        variants=variants,
        ean=raw.ean,
        purchase_price=raw.purchase_price,
        retail_price=retail,
    )


def _dedupe(items: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for it in items:
        if it not in seen:
            seen.add(it)
            out.append(it)
    return out
