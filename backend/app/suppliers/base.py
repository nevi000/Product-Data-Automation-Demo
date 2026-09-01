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
    input_format: str
    description: str

class SupplierAdapter(abc.ABC):
    meta: SupplierMeta
    @abc.abstractmethod
    def parse(self, payload: bytes) -> list[RawSupplierProduct]:
        """Parse a raw supplier document into raw products.

        Implementations must not raise on merely-incomplete data (that is the
        validator's job) — only on structurally unparseable input, as
        `SupplierParseError`.
        """
    @property
    def id(self) -> str:
        return self.meta.id

    @property
    def name(self) -> str:
        return self.meta.name