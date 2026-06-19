"""
build_invoice — PURE function that turns inputs into an Invoice dataclass.

⚠️ NO database calls here. No `datetime.now()`. No PDF. Just math.

The order is FIXED:
    1. base       = strategy.calculate(usage)
    2. discount   = discount.apply(base) if discount else 0
    3. taxable    = base - discount
    4. tax        = tax_calc.apply(taxable)
    5. total      = taxable + tax.total
"""

from __future__ import annotations

from datetime import date
from typing import Optional

from billing_engine.money import Money
from billing_engine.models import (
    Invoice, InvoiceStatus, InvoiceLineItem, LineItemKind, Subscription, Plan,
)
from billing_engine.pricing.base import PricingStrategy
from billing_engine.discounts.base import Discount, DiscountContext
from billing_engine.taxes.base import TaxCalculator, TaxContext


def build_invoice(
    subscription: Subscription,
    plan: Plan,
    strategy: PricingStrategy,
    discount: Optional[Discount],
    tax_calc: TaxCalculator,
    tax_context: TaxContext,
    usage_quantity: int,
    period_start: date,
    period_end: date,
    invoice_count_so_far: int,
) -> Invoice:
    base = strategy.calculate(usage_quantity)

    discount_total = Money.zero(plan.currency)
    if discount is not None:
        discount_total = discount.apply(
            base,
            DiscountContext(invoice_count_so_far=invoice_count_so_far),
        )

    taxable = base - discount_total
    tax_result = tax_calc.apply(taxable, tax_context)
    total = taxable + tax_result.total

    line_items = [
        InvoiceLineItem(
            id=None,
            invoice_id=None,
            description=plan.name,
            amount=base,
            kind=LineItemKind.BASE,
        )
    ]

    if discount_total > Money.zero(plan.currency):
        line_items.append(
            InvoiceLineItem(
                id=None,
                invoice_id=None,
                description="Discount",
                amount=-discount_total,
                kind=LineItemKind.DISCOUNT,
            )
        )

    for tax_desc, tax_amount in tax_result.components:
     line_items.append(
        InvoiceLineItem(
            id=None,
            invoice_id=None,
            description=tax_desc,
            amount=tax_amount,
            kind=LineItemKind.TAX,
        )
    )

    return Invoice(
        id=None,
        subscription_id=subscription.id,
        period_start=period_start,
        period_end=period_end,
        subtotal=base,
        discount_total=discount_total,
        tax_total=tax_result.total,
        total=total,
        status=InvoiceStatus.DRAFT,
        line_items=line_items,
    )
