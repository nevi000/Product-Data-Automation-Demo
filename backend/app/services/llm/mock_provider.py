from __future__ import annotations

import hashlib

from app.domain.models import NormalizedProduct
from app.services.llm.base import EnrichmentResult, LLMProvider

_OPENERS = [
    "Built for everyday wear",
    "A wardrobe staple with a considered cut",
    "Clean lines and a comfortable fit",
    "An easy layering piece",
    "Understated design, dependable construction",
]

_CLOSERS = [
    "Pairs well with the rest of the collection.",
    "Designed to hold its shape wash after wash.",
    "A quiet piece that works hard.",
    "Details you notice up close.",
]

_NAME_HINTS: dict[str, tuple[str, str]] = {
    "jacket": ("Product style", "Outdoor"),
    "shell": ("Product style", "Technical"),
    "fleece": ("Product style", "Outdoor"),
    "base layer": ("Fit", "Slim"),
    "beanie": ("Fit", "Regular"),
    "tee": ("Fit", "Regular"),
    "crew": ("Neckline", "Crew"),
    "half-zip": ("Neckline", "Half-zip"),
    "hooded": ("Neckline", "Hooded"),
    "cargo": ("Fit", "Relaxed"),
    "boxy": ("Fit", "Oversized"),
    "wide leg": ("Fit", "Relaxed"),
    "long sleeve": ("Sleeve length", "Long sleeve"),
}

_CATEGORY_HINTS: dict[str, str] = {
    "beanie": "Headwear",
    "hat": "Headwear",
    "cap": "Headwear",
    "glove": "Gloves",
    "mitt": "Gloves",
    "blanket": "Blankets",
    "throw": "Blankets",
    "bottle": "Drinkware",
    "flask": "Drinkware",
    "mug": "Drinkware",
    "tumbler": "Drinkware",
    "pack": "Bags",
    "backpack": "Bags",
    "tote": "Bags",
}

_MATERIAL_GUESS: dict[str, str] = {
    "jacket": "Recycled polyester shell, synthetic insulation",
    "shell": "3-layer waterproof laminate",
    "fleece": "Recycled polyester fleece",
    "beanie": "Lambswool",
    "boot": "Full-grain leather upper",
    "runner": "Engineered mesh upper",
    "trail": "Engineered mesh upper",
    "tee": "Organic cotton",
    "pant": "Cotton-nylon blend",
}

def _pick(options: list[str], seed: str) -> str:
    h = int(hashlib.sha256(seed.encode()).hexdigest(), 16)
    return options[h % len(options)]


class MockLLMProvider(LLMProvider):
    name = "mock"
    def enrich_product(
        self,
        product: NormalizedProduct,
        *,
        available_categories: list[str],
        available_properties: dict[str, list[str]],
        keywords: str = "",
    ) -> EnrichmentResult:
        seed = product.product_number
        name_l = product.name.lower()

        opener = _pick(_OPENERS, seed)
        closer = _pick(_CLOSERS, seed + "c")
        material = product.material or _guess_material(name_l)
        bits = [f"{opener}, the {product.name.lower()}"]
        if material:
            bits.append(f"is made from {material.lower()}")
        if product.color:
            bits.append(f"and comes in {product.color.lower()}")
        sentence = " ".join(bits).strip() + "."
        if keywords:
            sentence += f" Keywords: {keywords}."
        description = f"{sentence} {closer}"

        categories = _match_categories(product, available_categories, seed)

        properties: dict[str, str] = {}

        for opt in available_properties.get("Color", []):
            if product.color and opt.lower() == product.color.strip().lower():
                properties["Color"] = opt
                break

        for kw, (group, option) in _NAME_HINTS.items():
            if kw in name_l and group in available_properties:
                if option in available_properties[group]:
                    properties.setdefault(group, option)

        if "Sleeve length" in available_properties and "Sleeve length" not in properties:
            if any(w in name_l for w in ("tee", "top", "crew", "shirt")):
                properties["Sleeve length"] = "Short sleeve" if "tee" in name_l else "Long sleeve"

        return EnrichmentResult(
            description=description,
            categories=categories,
            properties=properties,
        )

def _guess_material(name_l: str) -> str | None:
    for kw, mat in _MATERIAL_GUESS.items():
        if kw in name_l:
            return mat
    return None

def _stem(token: str) -> str:
    return token[:-1] if token.endswith("s") and len(token) > 3 else token


def _tokens(text: str) -> set[str]:
    return {_stem(t) for t in text.lower().replace("-", " ").replace("/", " ").split()}


def _match_categories(
    product: NormalizedProduct, available: list[str], seed: str
) -> list[str]:
    name_tokens = _tokens(product.name)
    gender = ""
    if product.product_type:
        if product.product_type.startswith("womens"):
            gender = "women"
        elif product.product_type.startswith("mens"):
            gender = "men"

    name_l = product.name.lower()
    hinted = {frag for kw, frag in _CATEGORY_HINTS.items() if kw in name_l}

    opposite = {"women": "men", "men": "women"}.get(gender)

    scored: list[tuple[float, str]] = []
    for cat in available:
        segments = [s.strip() for s in cat.split("/")]
        leaf = segments[-1]
        path_tokens = _tokens(cat)
        if opposite and opposite in path_tokens:
            continue  # never suggest a wrong-gender category
        leaf_tokens = _tokens(leaf)
        score = 2 * len(name_tokens & leaf_tokens) + len(name_tokens & path_tokens)
        if leaf in hinted:
            score += 5
        if gender and gender in path_tokens:
            score += 0.5
        if score > 0:
            scored.append((score, cat))

    scored.sort(key=lambda t: (-t[0], t[1]))
    if not scored:
        return [_pick(available, seed + "cat")] if available else []

    top = scored[0][0]
    return [c for s, c in scored[:2] if s >= max(1.0, top * 0.5)]