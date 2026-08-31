from __future__ import annotations

from collections.abc import Callable, Iterable

from app.domain.models import NormalizedProduct, Severity, ValidationIssue

Rule = Callable[[NormalizedProduct], Iterable[ValidationIssue]]
_EAN_LENGTHS = {8, 12, 13, 14}

def _issue(field: str, sev: Severity, code: str, msg: str) -> ValidationIssue:
    return ValidationIssue(field=field, severity=sev, code=code, message=msg)

def rule_name(p: NormalizedProduct):
    if not p.name or not p.name.strip():
        yield _issue("name", Severity.ERROR, "name.missing", "Product name is empty.")
    elif len(p.name) > 120:
        yield _issue("name", Severity.WARNING, "name.too_long",
                     "Product name is longer than 120 characters.")

def rule_product_number(p: NormalizedProduct):
    if not p.product_number or p.product_number == "item":
        yield _issue("product_number", Severity.ERROR, "product_number.missing",
                     "Could not derive a product number from the supplier data.")

def rule_price(p: NormalizedProduct):
    if p.retail_price is None:
        yield _issue("retail_price", Severity.ERROR, "price.missing",
                     "No retail price and no purchase price to derive one from.")
        return
    if p.purchase_price and p.retail_price.amount <= p.purchase_price.amount:
        yield _issue("retail_price", Severity.WARNING, "price.margin",
                     "Retail price is not above purchase price.")

def rule_duplicate_sizes(p: NormalizedProduct):
    dupes = sorted(_dups(v.size for v in p.variants))
    if dupes:
        yield _issue("variants", Severity.ERROR, "variants.duplicate_size",
                     f"Duplicate sizes: {', '.join(dupes)}.")

def rule_eans(p: NormalizedProduct):
    for v in p.variants:
        if v.ean and not _valid_ean(v.ean):
            yield _issue(f"variants[{v.size}].ean", Severity.WARNING, "ean.format",
                         f"EAN {v.ean!r} for size {v.size} is not a plausible barcode.")
    if p.ean and not _valid_ean(p.ean):
        yield _issue("ean", Severity.WARNING, "ean.format",
                     f"EAN {p.ean!r} is not a plausible barcode.")

DEFAULT_RULES: list[Rule] = [
    rule_name,
    rule_product_number,
    rule_price,
    rule_duplicate_sizes,
    rule_eans,
]

def validate(
    product: NormalizedProduct, *, rules: list[Rule] = DEFAULT_RULES
) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    for rule in rules:
        issues.extend(rule(product))
    return issues

def _valid_ean(value: str) -> bool:
    #shape check only -> doesn't verify the EAN check digit
    return value.isdigit() and len(value) in _EAN_LENGTHS

def _dups(items: Iterable[str]) -> set[str]:
    seen: set[str] = set()
    out: set[str] = set()
    for it in items:
        if it in seen:
            out.add(it)
        seen.add(it)
    return out
