from __future__ import annotations

from decimal import Decimal

from pydantic import BaseModel

from app.domain.models import Money


class PricingPolicy(BaseModel):
    landed_cost_factor: Decimal = Decimal("1.15")
    retail_multiplier: Decimal = Decimal("2.5")
    round_to: Decimal = Decimal("1.00")

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
