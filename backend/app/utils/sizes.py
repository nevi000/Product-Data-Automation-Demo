from __future__ import annotations

SIZE_PRESETS: dict[str, list[str]] = {
    "womens_numeric": ["32", "34", "36", "38", "40", "42", "44", "46", "48"],
    "mens_numeric": ["44", "46", "48", "50", "52", "54", "56", "58", "60"],
    "alpha": ["XXS", "XS", "S", "M", "L", "XL", "XXL", "3XL"],
    "womens_shoes": ["36", "37", "38", "39", "40", "41", "42"],
    "mens_shoes": ["39", "40", "41", "42", "43", "44", "45", "46", "47"],
    "kids": ["98", "104", "110", "116", "128", "140", "152", "164"],
    "one_size": ["One Size"],
}

SIZE_PRESET_LABELS: dict[str, str] = {
    "womens_numeric": "Women's numeric (32–48)",
    "mens_numeric": "Men's numeric (44–60)",
    "alpha": "Alpha (XXS–3XL)",
    "womens_shoes": "Women's shoes (36–42)",
    "mens_shoes": "Men's shoes (39–47)",
    "kids": "Kids (98–164)",
    "one_size": "One size",
}

PRODUCT_TYPES: list[dict[str, str | None]] = [
    {"key": "womens_top", "label": "Women's top / knitwear", "size_preset": "alpha"},
    {"key": "womens_bottom", "label": "Women's trousers", "size_preset": "womens_numeric"},
    {"key": "womens_outerwear", "label": "Women's outerwear", "size_preset": "alpha"},
    {"key": "mens_top", "label": "Men's top / knitwear", "size_preset": "alpha"},
    {"key": "mens_bottom", "label": "Men's trousers", "size_preset": "mens_numeric"},
    {"key": "mens_outerwear", "label": "Men's outerwear", "size_preset": "alpha"},
    {"key": "womens_footwear", "label": "Women's footwear", "size_preset": "womens_shoes"},
    {"key": "mens_footwear", "label": "Men's footwear", "size_preset": "mens_shoes"},
    {"key": "kids", "label": "Kids", "size_preset": "kids"},
    {"key": "accessory", "label": "Accessory (one size)", "size_preset": "one_size"},
    {"key": "homeware", "label": "Home & travel (no sizes)", "size_preset": None},
]

_PRODUCT_TYPE_INDEX = {pt["key"]: pt for pt in PRODUCT_TYPES}

SIZE_CHARTS: list[dict[str, str]] = [
    {"id": "sc_womens_apparel", "name": "Women's Apparel"},
    {"id": "sc_mens_apparel", "name": "Men's Apparel"},
    {"id": "sc_womens_footwear", "name": "Women's Footwear (EU)"},
    {"id": "sc_mens_footwear", "name": "Men's Footwear (EU)"},
    {"id": "sc_base_layer", "name": "Base Layer Fit Guide"},
    {"id": "sc_outerwear", "name": "Outerwear Layering Guide"},
    {"id": "sc_headwear", "name": "Headwear"},
]

def preset_sizes(preset: str) -> list[str]:
    if preset not in SIZE_PRESETS:
        raise ValueError(f"Unknown size preset: {preset!r}")
    return list(SIZE_PRESETS[preset])

def size_range(preset: str, size_from: str, size_to: str) -> list[str]:
    sizes = preset_sizes(preset)
    if size_from not in sizes:
        raise ValueError(f"{size_from!r} is not in preset {preset!r}")
    if size_to not in sizes:
        raise ValueError(f"{size_to!r} is not in preset {preset!r}")
    i, j = sizes.index(size_from), sizes.index(size_to)
    if i > j:
        raise ValueError(f"{size_from!r} comes after {size_to!r} in {preset!r}")
    return sizes[i : j + 1]

def list_presets() -> list[dict[str, str]]:
    return sorted(
        ({"key": k, "label": SIZE_PRESET_LABELS[k]} for k in SIZE_PRESETS),
        key=lambda p: p["label"].lower(),
    )

def list_product_types() -> list[dict[str, str | None]]:
    return list(PRODUCT_TYPES)

def list_size_charts() -> list[dict[str, str]]:
    return list(SIZE_CHARTS)

def preset_for_product_type(product_type: str) -> str | None:
    pt = _PRODUCT_TYPE_INDEX.get(product_type)
    if pt is None:
        raise ValueError(f"Unknown product type: {product_type!r}")
    return pt["size_preset"]

def sizes_for_product_type(product_type: str) -> list[str]:
    preset = preset_for_product_type(product_type)
    return preset_sizes(preset) if preset else []
