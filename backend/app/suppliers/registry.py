"""Supplier registry.

Mirrors the production design: suppliers are *registered*, not hard-wired into
call sites. Everything else asks the registry for an adapter by id.
"""

from __future__ import annotations

from app.suppliers.alpinewear import AlpineWearAdapter
from app.suppliers.base import SupplierAdapter, SupplierMeta
from app.suppliers.demoshoes import DemoShoesAdapter
from app.suppliers.urbanthreads import UrbanThreadsAdapter


class SupplierRegistry:
    def __init__(self) -> None:
        self._adapters: dict[str, SupplierAdapter] = {}

    def register(self, adapter: SupplierAdapter) -> None:
        if adapter.id in self._adapters:
            raise ValueError(f"supplier {adapter.id!r} already registered")
        self._adapters[adapter.id] = adapter

    def get(self, supplier_id: str) -> SupplierAdapter:
        try:
            return self._adapters[supplier_id.lower()]
        except KeyError:
            raise KeyError(f"unknown supplier: {supplier_id!r}") from None

    def list(self) -> list[SupplierMeta]:
        return sorted(
            (a.meta for a in self._adapters.values()), key=lambda m: m.name.lower()
        )


registry = SupplierRegistry()
registry.register(AlpineWearAdapter())
registry.register(UrbanThreadsAdapter())
registry.register(DemoShoesAdapter())
