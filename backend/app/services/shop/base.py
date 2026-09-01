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
        """Return the id of a property option, creating it if it is needed."""

    @abc.abstractmethod
    def create_product(self, product: NormalizedProduct) -> ShopProduct:
        ...

    @abc.abstractmethod
    def get_product(self, product_number: str) -> ShopProduct | None:
        ...