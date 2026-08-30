"""Shop client boundary.

The production system writes to a Shopware 6 shop through its Admin API. This
interface is the generic version of that surface: read the taxonomy, resolve /
create property options idempotently, and create a product with variants.
"""

from __future__ import annotations

import abc

from pydantic import BaseModel

from app.domain.models import NormalizedProduct


class ShopWriteError(RuntimeError):
    pass


class ShopProduct(BaseModel):
    id: str
    product_number: str
    name: str
    variant_count: int
    category_paths: list[str] = []
    property_count: int = 0
    image_count: int = 0
    url: str
    # the full write payload the shop client would send — useful for the UI to
    # show "this is what would be created" without a real shop.
    payload: dict = {}


class ShopClient(abc.ABC):
    @abc.abstractmethod
    def list_category_paths(self) -> list[str]:
        ...

    @abc.abstractmethod
    def list_property_options(self) -> dict[str, list[str]]:
        ...

    @abc.abstractmethod
    def upsert_property_option(self, group: str, value: str) -> str:
        """Return the id of a property option, creating it if needed (idempotent)."""

    @abc.abstractmethod
    def create_product(self, product: NormalizedProduct) -> ShopProduct:
        ...

    @abc.abstractmethod
    def get_product(self, product_number: str) -> ShopProduct | None:
        ...
