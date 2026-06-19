"""
VATCalculator — single-rate VAT (e.g. 19% in Germany).
"""

from decimal import Decimal

from billing_engine.money import Money
from billing_engine.taxes.base import TaxCalculator, TaxContext, TaxBreakdown


class VATCalculator(TaxCalculator):
    def __init__(self, rate: Decimal) -> None:
        #   - Validate 0 <= rate <= 1.
        #   - Reject float.
        #   - Store on self.
        if isinstance(rate, float):
            raise TypeError("rate must be Decimal, not float")
        if not isinstance(rate, Decimal):
            raise TypeError("rate must be a Decimal")
        if rate < Decimal("0") or rate > Decimal("1"):
            raise ValueError("rate must be between 0 and 1")

        self.rate = rate

    def apply(self, taxable: Money, context: TaxContext) -> TaxBreakdown:
        #   - vat = taxable * self.rate
        #   - Return TaxBreakdown with one component (f"VAT {percent}%", vat) and total = vat.
        #   - Tip: format the rate as a percentage cleanly.
        vat = taxable * self.rate
        percent = (self.rate * Decimal("100")).normalize()
        label = f"VAT {percent}%"

        return TaxBreakdown(
            components=[(label, vat)],
            total=vat,
        )
