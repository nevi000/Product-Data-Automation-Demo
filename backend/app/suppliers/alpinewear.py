"""AlpineWear — JSON API feed.

Cleanest of the three sources: a well-formed JSON array where each element is one
colourway with a nested size/EAN map. The adapter still has to cope with:

* prices given as strings with a currency suffix,
* a ``status`` field where anything but ``"active"`` must be skipped,
* sizes present as an object (size -> {ean, ...}) rather than a list.
"""

from __future__ import annotations

import json
from decimal import Decimal, InvalidOperation

from app.domain.models import Money, RawSupplierProduct
from app.suppliers.base import SupplierAdapter, SupplierMeta, SupplierParseError

_CURRENCY_SUFFIX = {"EUR": "EUR", "€": "EUR", "CHF": "CHF", "USD": "USD", "$": "USD"}


def _money(value) -> Money | None:
    if value in (None, "", 0):
        return None
    if isinstance(value, (int, float, Decimal)):
        return Money(amount=Decimal(str(value)))
    text = str(value).strip()
    currency = "EUR"
    for suffix, code in _CURRENCY_SUFFIX.items():
        if text.endswith(suffix):
            currency = code
            text = text[: -len(suffix)].strip()
            break
    text = text.replace(",", ".")
    try:
        return Money(amount=Decimal(text), currency=currency)
    except (InvalidOperation, ValueError):
        return None


class AlpineWearAdapter(SupplierAdapter):
    meta = SupplierMeta(
        id="alpinewear",
        name="AlpineWear",
        input_format="json",
        description="Outdoor & technical apparel. Delivers a JSON product feed.",
    )

    def parse(self, payload: bytes) -> list[RawSupplierProduct]:
        try:
            data = json.loads(payload)
        except json.JSONDecodeError as exc:
            raise SupplierParseError(f"invalid JSON: {exc}") from exc

        items = data.get("products") if isinstance(data, dict) else data
        if not isinstance(items, list):
            raise SupplierParseError("expected a list of products or {'products': [...]}")

        out: list[RawSupplierProduct] = []
        for row in items:
            if not isinstance(row, dict):
                continue
            if str(row.get("status", "active")).lower() != "active":
                continue

            sizes_field = row.get("sizes") or {}
            if isinstance(sizes_field, dict):
                sizes = list(sizes_field.keys())
                ean_by_size = {
                    s: str(v.get("ean"))
                    for s, v in sizes_field.items()
                    if isinstance(v, dict) and v.get("ean")
                }
            else:  # a bare list of sizes
                sizes = [str(s) for s in sizes_field]
                ean_by_size = {}

            out.append(
                RawSupplierProduct(
                    supplier_id=self.id,
                    source_reference=row.get("sku") or row.get("article_no"),
                    model_name=row.get("name") or row.get("model"),
                    collection=row.get("collection") or row.get("season"),
                    color_name=(row.get("color") or {}).get("name")
                    if isinstance(row.get("color"), dict)
                    else row.get("color"),
                    color_code=(row.get("color") or {}).get("code")
                    if isinstance(row.get("color"), dict)
                    else row.get("color_code"),
                    manufacturer=row.get("brand") or self.name,
                    material=row.get("material"),
                    care_instructions=row.get("care") or row.get("care_instructions"),
                    sizes=sizes,
                    ean_by_size=ean_by_size,
                    ean=row.get("ean"),
                    purchase_price=_money(row.get("wholesale_price")),
                    suggested_retail_price=_money(row.get("rrp")),
                    raw=row,
                )
            )
        return out
