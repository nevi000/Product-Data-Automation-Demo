from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.services.shop import get_shop
from app.utils.sizes import (
    list_presets,
    list_product_types,
    list_size_charts,
    preset_sizes,
    sizes_for_product_type,
)

router = APIRouter()

@router.get("/categories")
def categories() -> list[str]:
    return get_shop().list_category_paths()

@router.get("/properties")
def properties() -> dict[str, list[str]]:
    return get_shop().list_property_options()

@router.get("/product-types")
def product_types() -> list[dict]:
    return list_product_types()

@router.get("/size-charts")
def size_charts() -> list[dict]:
    return list_size_charts()

@router.get("/size-presets")
def size_presets() -> list[dict]:
    return list_presets()

@router.get("/size-presets/{preset}")
def sizes_for_preset(preset: str) -> dict:
    try:
        return {"preset": preset, "sizes": preset_sizes(preset)}
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from None

@router.get("/product-types/{product_type}/sizes")
def sizes_for_type(product_type: str) -> dict:
    try:
        return {"product_type": product_type, "sizes": sizes_for_product_type(product_type)}
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from None
