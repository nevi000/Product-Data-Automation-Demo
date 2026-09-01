from __future__ import annotations

import csv
import io
from collections import OrderedDict
from decimal import Decimal, InvalidOperation

from app.domain.models import Money, RawSupplierProduct
from app.suppliers.base import SupplierAdapter, SupplierMeta, SupplierParseError
from app.utils.text import clean_number

_SKIP_ARTICLES = {"SHIPPING", "HANDLING", "FREIGHT"}

def _money(value: str | None) -> Money | None:
    if not value:
        return None
    try:
        amount = Decimal(clean_number(value))
    except (InvalidOperation, ValueError):
        return None
    if amount <= 0:
        return None
    return Money(amount=amount)

class UrbanThreadsAdapter(SupplierAdapter):
    meta = SupplierMeta(
        id="urbanthreads",
        name="UrbanThreads",
        input_format="csv",
        description="Streetwear label. Delivers a per-size CSV export.",
    )

    _REQUIRED = {"article_no", "size"}

    def parse(self, payload: bytes) -> list[RawSupplierProduct]:
        text = payload.decode("utf-8-sig")
        reader = csv.DictReader(io.StringIO(text), delimiter=";")
        if reader.fieldnames is None or not self._REQUIRED.issubset(
            {(f or "").strip() for f in reader.fieldnames}
        ):
            raise SupplierParseError(
                f"CSV must have at least columns {sorted(self._REQUIRED)}, "
                f"got {reader.fieldnames}"
            )

        # group_key -> RawSupplierProduct (built incrementally)
        grouped: OrderedDict[tuple[str, str], RawSupplierProduct] = OrderedDict()

        for row in reader:
            row = {(k or "").strip(): (v or "").strip() for k, v in row.items()}
            article = row.get("article_no", "")
            if not article or article.upper() in _SKIP_ARTICLES:
                continue
            try:
                if int(row.get("quantity", "1") or "1") <= 0:
                    continue
            except ValueError:
                pass  # keep the row if quantity is unparseable

            color_code = row.get("color_code", "")
            color_name = row.get("color_name", "")
            key = (article, color_code or color_name)

            product = grouped.get(key)
            if product is None:
                product = RawSupplierProduct(
                    supplier_id=self.id,
                    source_reference=article,
                    model_name=row.get("description") or article,
                    collection=row.get("collection") or None,
                    color_name=color_name or None,
                    color_code=color_code or None,
                    manufacturer=row.get("brand") or self.name,
                    material=row.get("material") or None,
                    care_instructions=row.get("care") or None,
                    purchase_price=_money(row.get("net_price")),
                    suggested_retail_price=_money(row.get("srp")),
                    raw={"rows": []},
                )
                grouped[key] = product

            size = row.get("size", "")
            if size and size not in product.sizes:
                product.sizes.append(size)
            ean = row.get("ean", "")
            if size and ean:
                product.ean_by_size[size] = ean
            product.raw["rows"].append(row)

        return list(grouped.values())