from __future__ import annotations

import uuid

from app.domain.models import NormalizedProduct
from app.services.shop.base import ShopClient, ShopProduct, ShopWriteError

_BASE_URL = "https://demo-shop.local/admin"

_CATEGORIES = [
    "Home / Women / Outerwear / Insulated Jackets",
    "Home / Women / Outerwear / Shell Jackets",
    "Home / Women / Outerwear / Fleece & Midlayers",
    "Home / Women / Base Layers / Tops",
    "Home / Women / Base Layers / Bottoms",
    "Home / Women / Knitwear",
    "Home / Women / Trousers",
    "Home / Men / Outerwear / Insulated Jackets",
    "Home / Men / Outerwear / Shell Jackets",
    "Home / Men / Outerwear / Fleece & Midlayers",
    "Home / Men / Base Layers / Tops",
    "Home / Men / Knitwear",
    "Home / Men / Trousers",
    "Home / Footwear / Trail Running",
    "Home / Footwear / Hiking Boots",
    "Home / Footwear / Everyday",
    "Home / Accessories / Headwear",
    "Home / Accessories / Gloves & Mitts",
    "Home / Accessories / Bags & Packs",
    "Home / Home & Travel / Blankets & Throws",
    "Home / Home & Travel / Drinkware",
]

_PROPERTY_OPTIONS = {
    "Color": [
        "Black", "Navy", "Slate Grey", "Charcoal", "Forest Green", "Rust",
        "Sand", "Bone", "Olive", "Off-White",
    ],
    "Fit": ["Slim", "Regular", "Relaxed", "Oversized"],
    "Sleeve length": ["Sleeveless", "Short sleeve", "3/4 sleeve", "Long sleeve"],
    "Product style": ["Casual", "Technical", "Outdoor", "Performance", "Loungewear"],
    "Neckline": ["Crew", "V-neck", "Half-zip", "Full-zip", "Hooded"],
}

def _new_id() -> str:
    return uuid.uuid4().hex

class MockShopAdapter(ShopClient):
    def __init__(self) -> None:
        self._options: dict[str, dict[str, str]] = {
            g: {v.lower(): _new_id() for v in vals}
            for g, vals in _PROPERTY_OPTIONS.items()
        }
        self._products: dict[str, ShopProduct] = {}

    def list_category_paths(self) -> list[str]:
        return list(_CATEGORIES)

    def list_property_options(self) -> dict[str, list[str]]:
        return {g: list(v) for g, v in _PROPERTY_OPTIONS.items()}

    def get_product(self, product_number: str) -> ShopProduct | None:
        return self._products.get(product_number)

    def upsert_property_option(self, group: str, value: str) -> str:
        bucket = self._options.setdefault(group, {})
        key = value.strip().lower()
        if key not in bucket:
            bucket[key] = _new_id()
        return bucket[key]

    def create_product(self, product: NormalizedProduct) -> ShopProduct:
        if not product.name.strip():
            raise ShopWriteError("cannot create a product without a name")
        if product.retail_price is None:
            raise ShopWriteError("cannot create a product without a retail price")
        if not product.categories:
            raise ShopWriteError("cannot create a product without a category")
        if product.product_number in self._products:
            raise ShopWriteError(
                f"product {product.product_number!r} already exists"
            )

        payload = self._build_payload(product)
        shop_product = ShopProduct(
            id=payload["id"],
            product_number=product.product_number,
            name=product.name,
            variant_count=len(payload["children"]),
            category_paths=product.categories,
            property_count=len(payload["properties"]),
            image_count=len(product.image_urls),
            url=f"{_BASE_URL}/product/{payload['id']}",
            payload=payload,
        )
        self._products[product.product_number] = shop_product
        return shop_product

    def _build_payload(self, product: NormalizedProduct) -> dict:
        parent_id = _new_id()

        size_option_ids = {
            v.size: self.upsert_property_option("Size", v.size)
            for v in product.active_variants
        }
        children = [
            {
                "id": _new_id(),
                "productNumber": f"{product.product_number}.{i}",
                "stock": 0,
                "active": False,
                "options": [{"id": size_option_ids[v.size]}],
                **({"ean": v.ean} if v.ean else {}),
            }
            for i, v in enumerate(product.active_variants, start=1)
        ]

        properties = [
            {"group": group, "value": value, "id": self.upsert_property_option(group, value)}
            for group, value in product.properties.items()
        ]
        if product.material:
            properties.append({
                "group": "Material", "value": product.material,
                "id": self.upsert_property_option("Material", product.material),
            })
        if product.care_instructions:
            properties.append({
                "group": "Care", "value": product.care_instructions,
                "id": self.upsert_property_option("Care", product.care_instructions),
            })

        payload: dict = {
            "id": parent_id,
            "productNumber": product.product_number,
            "name": product.name,
            "description": product.description or "",
            "manufacturer": product.manufacturer.name if product.manufacturer else None,
            "productType": product.product_type,
            "sizeChartId": product.size_chart,
            "stock": 0,
            "active": False,
            "price": [{"gross": float(product.retail_price.amount),
                       "currency": product.retail_price.currency}],
            "categories": [{"path": p} for p in product.categories],
            "properties": properties,
            "children": children,
            "configuratorSettings": [
                {"id": _new_id(), "optionId": oid}
                for oid in size_option_ids.values()
            ],
            "media": [{"url": u, "position": i}
                      for i, u in enumerate(product.image_urls)],
        }
        if product.purchase_price:
            payload["purchasePrice"] = {
                "gross": float(product.purchase_price.amount),
                "currency": product.purchase_price.currency,
            }
        if product.ean:
            payload["ean"] = product.ean
        return payload