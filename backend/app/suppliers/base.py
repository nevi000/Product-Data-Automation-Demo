"""Supplier adapter abstraction.

Every supplier delivers product data in its own format — a JSON API dump, a CSV
export, an HTML catalogue page, a PDF order confirmation. An adapter's only job
is to turn *one* of those formats into a list of `RawSupplierProduct`.

Adding a supplier = one new `SupplierAdapter` subclass + one registry entry.
Nothing downstream (normalization, validation, enrichment, export) changes.

In the production system there are 20+ such adapters. This repo ships 3, in 3
deliberately different formats, to show the abstraction holds.
"""

from __future__ import annotations

import abc
from dataclasses import dataclass

from app.domain.models import RawSupplierProduct


class SupplierParseError(ValueError):
    """Raised when an input document cannot be parsed for the given supplier."""


@dataclass(frozen=True)
class SupplierMeta:
    id: str
    name: str
    input_format: str            # "json" | "csv" | "html"
    description: str


class SupplierAdapter(abc.ABC):
    """Base class for all supplier adapters."""

    meta: SupplierMeta

    @abc.abstractmethod
    def parse(self, payload: bytes) -> list[RawSupplierProduct]:
        """Parse a raw supplier document into raw products.

        Implementations must not raise on merely-incomplete data (that is the
        validator's job) — only on structurally unparseable input, as
        `SupplierParseError`.
        """

    # convenience so callers don't need to know the concrete class
    @property
    def id(self) -> str:
        return self.meta.id

    @property
    def name(self) -> str:
        return self.meta.name
