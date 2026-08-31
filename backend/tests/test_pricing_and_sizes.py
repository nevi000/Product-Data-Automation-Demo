from decimal import Decimal

import pytest

from app.domain.models import Money
from app.domain.pricing import PricingPolicy
from app.utils.sizes import list_presets, preset_sizes, size_range


def test_pricing_rounds_to_whole_units():
    policy = PricingPolicy(
        landed_cost_factor=Decimal("1.15"),
        retail_multiplier=Decimal("2.5"),
        round_to=Decimal("1.00"),
    )
    out = policy.suggest_retail(Money(amount=Decimal("39.50")))
    # 39.50 * 1.15 * 2.5 = 113.5625 -> 114
    assert out == Money(amount=Decimal("114"))


def test_pricing_none_in_none_out():
    assert PricingPolicy().suggest_retail(None) is None


def test_size_range_slice_inclusive():
    assert size_range("alpha", "S", "L") == ["S", "M", "L"]


def test_size_range_rejects_reversed_bounds():
    with pytest.raises(ValueError):
        size_range("alpha", "L", "S")


def test_size_range_rejects_unknown_size():
    with pytest.raises(ValueError):
        size_range("alpha", "S", "XXXL")


def test_presets_are_listed_with_labels():
    presets = list_presets()
    assert {"key": "alpha", "label": "Alpha (XXS–3XL)"} in presets
    assert preset_sizes("one_size") == ["One Size"]
