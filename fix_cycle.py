from pathlib import Path
from textwrap import dedent

path = Path('billing_engine_starter/billing_engine/billing/cycle.py')
contents = dedent('''
"""
BillingCycle — finds due subscriptions, generates invoices, posts ledger DEBITs,
advances the subscription period. Must be IDEMPOTENT (safe to run twice).
"""

from __future__ import annotations

import sqlite3
from calendar import monthrange
from dataclasses import dataclass
from datetime import date
from typing import Callable

from billing_engine.billing.pipeline import build_invoice
from billing_engine.billing.proration import compute_proration
from billing_engine.db import (
    Database,
    CustomerRepository, PlanRepository, SubscriptionRepository,
    UsageRecordRepository, InvoiceRepository, InvoiceLineItemRepository,
    LedgerRepository,
)
from billing_engine.models import (
    BillingPeriod,
    Invoice,
    InvoiceLineItem,
    InvoiceStatus,
    LedgerDirection,
    LedgerEntry,
    LineItemKind,
    Plan,
    Subscription,
    SubscriptionStatus,
)
from billing_engine.money import Money


@dataclass
class BillingResult:
    invoices_created: int
    invoices_skipped_duplicate: int
    trials_activated: int


class BillingCycle:
    """Day-3 deliverable. Day-4 stretch: add `upgrade_subscription(...)`."""

    def __init__(
        self,
        db: Database,
        customer_repo: CustomerRepository,
        plan_repo: PlanRepository,
        subscription_repo: SubscriptionRepository,
        usage_repo: UsageRecordRepository,
        invoice_repo: InvoiceRepository,
        line_item_repo: InvoiceLineItemRepository,
        ledger_repo: LedgerRepository,
        strategy_factory: Callable,
        discount_factory: Callable,
        tax_factory: Callable,
    ) -> None:
        self.db = db
        self.customer_repo = customer_repo
        self.plan_repo = plan_repo
        self.subscription_repo = subscription_repo
        self.usage_repo = usage_repo
        self.invoice_repo = invoice_repo
        self.line_item_repo = line_item_repo
        self.ledger_repo = ledger_repo
        self.strategy_factory = strategy_factory
        self.discount_factory = discount_factory
        self.tax_factory = tax_factory

    @staticmethod
    def _add_months(value: date, months: int) -> date:
        month_index = value.month - 1 + months
        year = value.year + month_index // 12
        month = month_index % 12 + 1
        day = min(value.day, monthrange(year, month)[1])
        return date(year, month, day)

    def _usage_quantity_for(self, subscription: Subscription) -> int:
        if subscription.id is None:
            return 0
        return self.usage_repo.sum_for_period(
            subscription.id,
            'usage',
            subscription.current_period_start,
            subscription.current_period_end,
        )

    def _calculate_plan_price(self, plan: Plan, subscription: Subscription) -> Money:
        strategy = self.strategy_factory(plan)
        quantity = self._usage_quantity_for(subscription)
        return strategy.calculate(quantity)

    # --------------------------------------------------------
    def run(self, as_of: date) -> BillingResult:
        invoices_created = 0
        invoices_skipped_duplicate = 0
        trials_activated = 0

        for sub in self.subscription_repo.list_all():
            if (
                sub.status == SubscriptionStatus.TRIAL
                and sub.trial_end is not None
                and sub.trial_end <= as_of
            ):
                self.subscription_repo.update_status(sub.id, SubscriptionStatus.ACTIVE)
                trials_activated += 1

        due = self.subscription_repo.get_due_for_billing(as_of)
        for sub in due:
            customer = self.customer_repo.get(sub.customer_id)
            if customer is None:
                continue
            plan = self.plan_repo.get(sub.plan_id)
            if plan is None:
                continue

            discount = None
            if sub.discount_id is not None:
                discount = self.discount_factory(sub.discount_id)

            strategy = self.strategy_factory(plan)
            tax_calc, tax_context = self.tax_factory(customer)
            invoice_count_so_far = self.invoice_repo.count_for_subscription(sub.id)
            quantity = self._usage_quantity_for(sub)

            invoice = build_invoice(
                subscription=sub,
                plan=plan,
                strategy=strategy,
                discount=discount,
                tax_calc=tax_calc,
                tax_context=tax_context,
                usage_quantity=quantity,
                period_start=sub.current_period_start,
                period_end=sub.current_period_end,
                invoice_count_so_far=invoice_count_so_far,
            )

            try:
                invoice = self.invoice_repo.add(invoice)
            except sqlite3.IntegrityError:
                invoices_skipped_duplicate += 1
                continue

            for line_item in invoice.line_items:
                self.line_item_repo.add(
                    InvoiceLineItem(
                        id=None,
                        invoice_id=invoice.id,
                        description=line_item.description,
                        amount=line_item.amount,
                        kind=line_item.kind,
                    )
                )

            self.ledger_repo.add(
                LedgerEntry(
                    id=None,
                    invoice_id=invoice.id,
                    customer_id=customer.id,
                    amount=invoice.total,
                    direction=LedgerDirection.DEBIT,
                    reason=f'Invoice {invoice.id} for subscription {sub.id}',
                )
            )

            if plan.billing_period == BillingPeriod.YEARLY:
                next_start = sub.current_period_end
                next_end = date(
                    sub.current_period_end.year + 1,
                    sub.current_period_end.month,
                    sub.current_period_end.day,
                )
            else:
                next_start = sub.current_period_end
                next_end = self._add_months(sub.current_period_end, 1)

            self.subscription_repo.update_period(sub.id, next_start, next_end)
            invoices_created += 1

        return BillingResult(
            invoices_created=invoices_created,
            invoices_skipped_duplicate=invoices_skipped_duplicate,
            trials_activated=trials_activated,
        )

    # --------------------------------------------------------
    def upgrade_subscription(
        self,
        subscription_id: int,
        new_plan_id: int,
        switch_date: date,
    ) -> None:
        """Mid-cycle upgrade — Day 4 stretch."""
        subscription = self.subscription_repo.get(subscription_id)
        if subscription is None:
            raise ValueError(f'Unknown subscription {subscription_id}')

        old_plan = self.plan_repo.get(subscription.plan_id)
        if old_plan is None:
            raise ValueError(f'Unknown plan {subscription.plan_id}')

        new_plan = self.plan_repo.get(new_plan_id)
        if new_plan is None:
            raise ValueError(f'Unknown plan {new_plan_id}')

        customer = self.customer_repo.get(subscription.customer_id)
        if customer is None:
            raise ValueError(f'Unknown customer {subscription.customer_id}')

        old_price = self._calculate_plan_price(old_plan, subscription)
        new_price = self._calculate_plan_price(new_plan, subscription)

        tax_calc, tax_context = self.tax_factory(customer)
        proration = compute_proration(
            old_plan_price=old_price,
            new_plan_price=new_price,
            period_start=subscription.current_period_start,
            period_end=subscription.current_period_end,
            switch_date=switch_date,
            tax_calc=tax_calc,
            tax_context=tax_context,
        )

        subtotal = proration.charge_amount - proration.credit_amount
        tax_total = proration.charge_tax - proration.credit_tax
        total = subtotal + tax_total

        proration_invoice = Invoice(
            id=None,
            subscription_id=subscription.id,
            period_start=subscription.current_period_start,
            period_end=subscription.current_period_end,
            subtotal=subtotal,
            discount_total=Money.zero(new_plan.currency),
            tax_total=tax_total,
            total=total,
            status=InvoiceStatus.ISSUED,
            line_items=[],
        )
        proration_invoice = self.invoice_repo.add(proration_invoice)

        line_items = [
            InvoiceLineItem(
                id=None,
                invoice_id=proration_invoice.id,
                description=f'Proration credit for {old_plan.name}',
                amount=-proration.credit_amount,
                kind=LineItemKind.PRORATION_CREDIT,
            ),
            InvoiceLineItem(
                id=None,
                invoice_id=proration_invoice.id,
                description=f'Proration charge for {new_plan.name}',
                amount=proration.charge_amount,
                kind=LineItemKind.PRORATION_CHARGE,
            ),
        ]

        if proration.credit_tax.is_positive():
            line_items.append(
                InvoiceLineItem(
                    id=None,
                    invoice_id=proration_invoice.id,
                    description=f'Proration tax reversal for {old_plan.name}',
                    amount=-proration.credit_tax,
                    kind=LineItemKind.TAX,
                )
            )
        if proration.charge_tax.is_positive():
            line_items.append(
                InvoiceLineItem(
                    id=None,
                    invoice_id=proration_invoice.id,
                    description=f'Proration tax for {new_plan.name}',
                    amount=proration.charge_tax,
                    kind=LineItemKind.TAX,
                )
            )

        for item in line_items:
            self.line_item_repo.add(item)

        self.ledger_repo.add(
            LedgerEntry(
                id=None,
                invoice_id=proration_invoice.id,
                customer_id=customer.id,
                amount=proration_invoice.total,
                direction=LedgerDirection.DEBIT,
                reason=f'Proration upgrade to {new_plan.name}',
            )
        )

        self.subscription_repo.update_plan(subscription_id, new_plan_id)
''').strip() + '\n'

path.write_text(contents, encoding='utf-8')
print(f'wrote {path}')
print(contents.splitlines()[:40])
