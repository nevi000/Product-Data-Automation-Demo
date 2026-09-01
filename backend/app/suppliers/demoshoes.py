from __future__ import annotations

from decimal import Decimal, InvalidOperation
from html.parser import HTMLParser

from app.domain.models import Money, RawSupplierProduct
from app.suppliers.base import SupplierAdapter, SupplierMeta, SupplierParseError
from app.utils.text import clean_number


def _money(value: str | None) -> Money | None:
    if not value:
        return None
    text = value.replace("€", "").replace("EUR", "").strip()
    try:
        return Money(amount=Decimal(clean_number(text)))
    except (InvalidOperation, ValueError):
        return None

class _CatalogueParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.rows: list[dict] = []
        self._in_product_row = False
        self._in_size_row = False
        self._cell: list[str] = []
        self._cells: list[str] = []
        self._current: dict | None = None
        self._size_attrs: dict | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        a = dict(attrs)
        if tag == "tr":
            cls = (a.get("class") or "")
            self._in_product_row = "product" in cls
            self._in_size_row = "sizes" in cls
            self._cells = []
        elif tag == "td":
            self._cell = []
            self._size_attrs = a if self._in_size_row else None

    def handle_data(self, data: str) -> None:
        if self._in_product_row or self._in_size_row:
            self._cell.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag == "td":
            text = "".join(self._cell).strip()
            if self._in_product_row:
                self._cells.append(text)
            elif self._in_size_row and self._current is not None:
                a = self._size_attrs or {}
                cls = a.get("class") or ""
                if text and "sold-out" not in cls:
                    self._current["sizes"].append(text)
                    if a.get("data-ean"):
                        self._current["ean_by_size"][text] = a["data-ean"]
        elif tag == "tr":
            if self._in_product_row and len(self._cells) >= 4:
                self._current = {
                    "article": self._cells[0],
                    "model": self._cells[1],
                    "color": self._cells[2],
                    "price": self._cells[3],
                    "collection": self._cells[4] if len(self._cells) > 4 else None,
                    "sizes": [],
                    "ean_by_size": {},
                }
                self.rows.append(self._current)
            self._in_product_row = self._in_size_row = False

class DemoShoesAdapter(SupplierAdapter):
    meta = SupplierMeta(
        id="demoshoes",
        name="DemoShoes",
        input_format="html",
        description="Footwear wholesaler. Only source is a B2B catalogue HTML page.",
    )

    def parse(self, payload: bytes) -> list[RawSupplierProduct]:
        parser = _CatalogueParser()
        try:
            parser.feed(payload.decode("utf-8"))
        except Exception as exc:  # pragma: no cover - html.parser is lenient
            raise SupplierParseError(f"could not parse HTML: {exc}") from exc

        if not parser.rows:
            raise SupplierParseError(
                "no <tr class='product'> rows found — is this the catalogue page?"
            )

        out: list[RawSupplierProduct] = []
        for row in parser.rows:
            out.append(
                RawSupplierProduct(
                    supplier_id=self.id,
                    source_reference=row["article"] or None,
                    model_name=row["model"] or None,
                    collection=row.get("collection"),
                    color_name=(row["color"] or "").lower() or None,
                    manufacturer=self.name,
                    sizes=row["sizes"],
                    ean_by_size=row["ean_by_size"],
                    purchase_price=_money(row["price"]),
                    raw=row,
                )
            )
        return out