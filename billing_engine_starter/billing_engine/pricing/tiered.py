"""
TieredPricing — different price per unit depending on the tier the quantity falls into.

This is the "cumulative" / "stacked" tier model, NOT the "volume" model:
    Tiers: [(0, 1000, ₹2.00), (1000, 5000, ₹1.50), (5000, None, ₹1.00)]
    Quantity = 6000:
        First 1000 units  @ ₹2.00 = ₹2000
        Next  4000 units  @ ₹1.50 = ₹6000
        Last  1000 units  @ ₹1.00 = ₹1000
        ------------------------------------
        Total                     = ₹9000

A tier with `to_units = None` is the open-ended top tier.

Tier boundaries are HALF-OPEN on the right: a tier (from, to, price)
covers units strictly less than `to` (i.e. [from, to)).
"""

from dataclasses import dataclass
from typing import Optional

from billing_engine.money import Money
from billing_engine.pricing.base import PricingStrategy


@dataclass(frozen=True)
class Tier:
    from_units: int
    to_units: Optional[int]   # None means "unlimited" / open-ended
    unit_price: Money


class TieredPricing(PricingStrategy):
    """Charges across multiple price tiers based on cumulative quantity."""

    def __init__(self, tiers: list[Tier]) -> None:
        if not tiers:
            raise ValueError("tiers must not be empty")

        expected_from = 0
        seen_open_ended = False
        currency = tiers[0].unit_price.currency

        for i, tier in enumerate(tiers):
            if tier.from_units < 0:
                raise ValueError("from_units must be non-negative")
            if not isinstance(tier.unit_price, Money):
                raise TypeError("unit_price must be Money")
            if tier.unit_price.currency != currency:
                raise ValueError("all tiers must use same currency")
            if tier.unit_price.amount < 0:
                raise ValueError("unit_price must be non-negative")
            if tier.from_units != expected_from:
                raise ValueError("tiers must be contiguous and ordered")

            if tier.to_units is None:
                seen_open_ended = True
                if i != len(tiers) - 1:
                    raise ValueError("open-ended tier must be last")
            else:
                if seen_open_ended:
                    raise ValueError("no tiers allowed after open-ended tier")
                if tier.to_units <= tier.from_units:
                    raise ValueError("to_units must be greater than from_units")
                expected_from = tier.to_units

        if tiers[-1].to_units is not None:
            raise ValueError("top tier must be open-ended")

        self.tiers = tiers
        self.currency = currency

    def calculate(self, quantity: int) -> Money:
        if quantity < 0:
            raise ValueError("quantity must be non-negative")

        total = Money.zero(self.currency)

        for tier in self.tiers:
            if quantity <= tier.from_units:
                break

            upper = quantity if tier.to_units is None else min(quantity, tier.to_units)
            units_in_tier = upper - tier.from_units

            if units_in_tier > 0:
                total = total + (tier.unit_price * units_in_tier)

        return total