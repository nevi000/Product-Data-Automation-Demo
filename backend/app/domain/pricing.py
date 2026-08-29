"""Pricing policy.

The production system applies a company-specific pricing rule to turn a
supplier's purchase price into a shop retail price. That exact rule (and the
numbers behind it) is proprietary and is **not** reproduced here.

What is reproduced is the *engineering shape*: a small, explicit, configurable
policy object so the rule lives in one place, is unit-testable, and can be
overridden per supplier. The constants below are illustrative placeholders.
"""

from __future__ import annotations

from decimal import Decimal

from pydantic import BaseModel

from app.domain.models import Money


class PricingPolicy(BaseModel):
    """Turns a purchase price into a suggested retail price.

    retail = purchase * landed_cost_factor * retail_multiplier

    * ``landed_cost_factor`` — placeholder for duty/freight/handling uplift.
    * ``retail_multiplier``  — placeholder for the gross margin target.

    These are *demo* numbers. Real figures are configuration, never code, and are
    out of scope for this portfolio repository.
    """

    landed_cost_factor: Decimal = Decimal("1.15")
    retail_multiplier: Decimal = Decimal("2.5")
    round_to: Decimal = Decimal("1.00")   # round suggested retail to whole units

    def suggest_retail(self, purchase: Money | None) -> Money | None:
        if purchase is None:
            return None
        raw = purchase.amount * self.landed_cost_factor * self.retail_multiplier
        rounded = (raw / self.round_to).to_integral_value() * self.round_to
        return Money(amount=rounded, currency=purchase.currency)

    def landed_cost(self, purchase: Money | None) -> Money | None:
        if purchase is None:
            return None
        return Money(
            amount=purchase.amount * self.landed_cost_factor,
            currency=purchase.currency,
        )


DEFAULT_PRICING = PricingPolicy()
