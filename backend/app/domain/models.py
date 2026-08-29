from __future__ import annotations

from decimal import Decimal
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, computed_field, field_validator


class Money(BaseModel):
    amount: Decimal = Field(ge=0)
    currency: str = "EUR"

    @field_validator("amount")
    @classmethod
    def _quantize(cls, v: Decimal) -> Decimal:
        return v.quantize(Decimal("0.01"))

    def __str__(self) -> str: 
        return f"{self.amount} {self.currency}"


class ManufacturerRef(BaseModel):
    name: str
    external_id: str | None = None


class RawSupplierProduct(BaseModel):
    #Output of a `SupplierAdapter`.

    model_config = ConfigDict(protected_namespaces=())
    supplier_id: str
    source_reference: str | None = None 
    model_name: str | None = None
    collection: str | None = None
    color_name: str | None = None
    color_code: str | None = None
    manufacturer: str | None = None
    material: str | None = None
    sizes: list[str] = Field(default_factory=list)
    ean_by_size: dict[str, str] = Field(default_factory=dict)
    ean: str | None = None
    care_instructions: str | None = None
    purchase_price: Money | None = None
    suggested_retail_price: Money | None = None
    #untouched source row, for debugging
    raw: dict = Field(default_factory=dict)       


class Variant(BaseModel):
    size: str
    ean: str | None = None
    active: bool = True


class NormalizedProduct(BaseModel):
    # supplier data
    supplier_id: str
    product_number: str
    source_reference: str | None = None
    name: str
    collection: str | None = None
    color: str | None = None
    manufacturer: ManufacturerRef | None = None
    material: str | None = None
    variants: list[Variant] = Field(default_factory=list)
    ean: str | None = None
    purchase_price: Money | None = None
    retail_price: Money | None = None

    #reviewer-set classification
    product_type: str | None = None
    size_chart: str | None = None 
    care_instructions: str | None = None

    #enrichment that are optional
    description: str | None = None
    categories: list[str] = Field(default_factory=list)
    properties: dict[str, str] = Field(default_factory=dict)
    image_urls: list[str] = Field(default_factory=list)

    @property
    def has_sizes(self) -> bool:
        return len(self.variants) > 0

    @property
    def active_variants(self) -> list[Variant]:
        # only the variants that are marked as active are returned
        return [v for v in self.variants if v.active]


class Severity(StrEnum):
    ERROR = "error"
    WARNING = "warning"


class ValidationIssue(BaseModel):
    field: str
    severity: Severity
    message: str
    code: str
    @computed_field
    @property
    def blocking(self) -> bool:
        return self.severity is Severity.ERROR

class ChecklistItem(BaseModel):
    key: str
    label: str
    done: bool
    required: bool = True


class ReviewProduct(BaseModel):
    product: NormalizedProduct
    issues: list[ValidationIssue] = Field(default_factory=list)
    checklist: list[ChecklistItem] = Field(default_factory=list)
    @computed_field
    @property
    #counts the number of required checklist items that aren't done
    def fields_remaining(self) -> int:
        return sum(1 for c in self.checklist if c.required and not c.done)

    @computed_field
    @property
    #returns true if there are no blocking issues and all required checklist items are done
    def exportable(self) -> bool:
        return not any(i.blocking for i in self.issues) and self.fields_remaining == 0


class SourceDocument(BaseModel):
    filename: str
    media_type: str
    extractor: str
    is_mock: bool = True
    note: str | None = None


class PipelineResult(BaseModel):
    supplier_id: str
    supplier_name: str
    source_reference: str | None = None
    source_document: SourceDocument | None = None
    raw_products: list[RawSupplierProduct]
    review_products: list[ReviewProduct]
    @computed_field
    @property
    def count(self) -> int:
        return len(self.review_products)
