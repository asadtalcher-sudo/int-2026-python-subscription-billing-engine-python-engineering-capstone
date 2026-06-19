"""
BillingCycle — finds due subscriptions, generates invoices, posts ledger DEBITs,
advances the subscription period. Must be IDEMPOTENT (safe to run twice).
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Callable, Optional

from billing_engine.db import (
    Database,
    CustomerRepository, PlanRepository, SubscriptionRepository,
    UsageRecordRepository, InvoiceRepository, InvoiceLineItemRepository,
    LedgerRepository,
)
from billing_engine.models import Subscription


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
        strategy_factory: Callable,    # given a Plan, returns a PricingStrategy
        discount_factory: Callable,    # given a discount_id or None, returns a Discount or None
        tax_factory: Callable,         # given a Customer, returns (TaxCalculator, TaxContext)
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

    # --------------------------------------------------------
    def run(self, as_of: date) -> BillingResult:
        [{
	"resource": "/C:/Users/Nikhat/OneDrive/Documents/GitHub/subscription-billing-engine-asadtalcher-sudo/billing_engine_starter/billing_engine/billing/cycle.py",
	"owner": "Pylance",
	"severity": 8,
	"message": "\"return\" can be used only within a function",
	"source": "Pylance",
	"startLineNumber": 161,
	"startColumn": 5,
	"endLineNumber": 161,
	"endColumn": 11,
	"modelVersionId": 79,
	"origin": "extHost1"
},{
	"resource": "/C:/Users/Nikhat/OneDrive/Documents/GitHub/subscription-billing-engine-asadtalcher-sudo/billing_engine_starter/billing_engine/billing/cycle.py",
	"owner": "Pylance",
	"code": {
		"value": "reportUndefinedVariable",
		"target": {
			"$mid": 1,
			"path": "/microsoft/pylance-release/blob/main/docs/diagnostics/reportUndefinedVariable.md",
			"scheme": "https",
			"authority": "github.com"
		}
	},
	"severity": 4,
	"message": "\"self\" is not defined",
	"source": "Pylance",
	"startLineNumber": 70,
	"startColumn": 16,
	"endLineNumber": 70,
	"endColumn": 20,
	"modelVersionId": 79,
	"origin": "extHost1"
},{
	"resource": "/C:/Users/Nikhat/OneDrive/Documents/GitHub/subscription-billing-engine-asadtalcher-sudo/billing_engine_starter/billing_engine/billing/cycle.py",
	"owner": "Pylance",
	"code": {
		"value": "reportUndefinedVariable",
		"target": {
			"$mid": 1,
			"path": "/microsoft/pylance-release/blob/main/docs/diagnostics/reportUndefinedVariable.md",
			"scheme": "https",
			"authority": "github.com"
		}
	},
	"severity": 4,
	"message": "\"as_of\" is not defined",
	"source": "Pylance",
	"startLineNumber": 74,
	"startColumn": 34,
	"endLineNumber": 74,
	"endColumn": 39,
	"modelVersionId": 79,
	"origin": "extHost1"
},{
	"resource": "/C:/Users/Nikhat/OneDrive/Documents/GitHub/subscription-billing-engine-asadtalcher-sudo/billing_engine_starter/billing_engine/billing/cycle.py",
	"owner": "Pylance",
	"code": {
		"value": "reportUndefinedVariable",
		"target": {
			"$mid": 1,
			"path": "/microsoft/pylance-release/blob/main/docs/diagnostics/reportUndefinedVariable.md",
			"scheme": "https",
			"authority": "github.com"
		}
	},
	"severity": 4,
	"message": "\"self\" is not defined",
	"source": "Pylance",
	"startLineNumber": 76,
	"startColumn": 13,
	"endLineNumber": 76,
	"endColumn": 17,
	"modelVersionId": 79,
	"origin": "extHost1"
},{
	"resource": "/C:/Users/Nikhat/OneDrive/Documents/GitHub/subscription-billing-engine-asadtalcher-sudo/billing_engine_starter/billing_engine/billing/cycle.py",
	"owner": "Pylance",
	"code": {
		"value": "reportUndefinedVariable",
		"target": {
			"$mid": 1,
			"path": "/microsoft/pylance-release/blob/main/docs/diagnostics/reportUndefinedVariable.md",
			"scheme": "https",
			"authority": "github.com"
		}
	},
	"severity": 4,
	"message": "\"self\" is not defined",
	"source": "Pylance",
	"startLineNumber": 79,
	"startColumn": 25,
	"endLineNumber": 79,
	"endColumn": 29,
	"modelVersionId": 79,
	"origin": "extHost1"
},{
	"resource": "/C:/Users/Nikhat/OneDrive/Documents/GitHub/subscription-billing-engine-asadtalcher-sudo/billing_engine_starter/billing_engine/billing/cycle.py",
	"owner": "Pylance",
	"code": {
		"value": "reportUndefinedVariable",
		"target": {
			"$mid": 1,
			"path": "/microsoft/pylance-release/blob/main/docs/diagnostics/reportUndefinedVariable.md",
			"scheme": "https",
			"authority": "github.com"
		}
	},
	"severity": 4,
	"message": "\"as_of\" is not defined",
	"source": "Pylance",
	"startLineNumber": 79,
	"startColumn": 68,
	"endLineNumber": 79,
	"endColumn": 73,
	"modelVersionId": 79,
	"origin": "extHost1"
},{
	"resource": "/C:/Users/Nikhat/OneDrive/Documents/GitHub/subscription-billing-engine-asadtalcher-sudo/billing_engine_starter/billing_engine/billing/cycle.py",
	"owner": "Pylance",
	"code": {
		"value": "reportUndefinedVariable",
		"target": {
			"$mid": 1,
			"path": "/microsoft/pylance-release/blob/main/docs/diagnostics/reportUndefinedVariable.md",
			"scheme": "https",
			"authority": "github.com"
		}
	},
	"severity": 4,
	"message": "\"self\" is not defined",
	"source": "Pylance",
	"startLineNumber": 82,
	"startColumn": 20,
	"endLineNumber": 82,
	"endColumn": 24,
	"modelVersionId": 79,
	"origin": "extHost1"
},{
	"resource": "/C:/Users/Nikhat/OneDrive/Documents/GitHub/subscription-billing-engine-asadtalcher-sudo/billing_engine_starter/billing_engine/billing/cycle.py",
	"owner": "Pylance",
	"code": {
		"value": "reportUndefinedVariable",
		"target": {
			"$mid": 1,
			"path": "/microsoft/pylance-release/blob/main/docs/diagnostics/reportUndefinedVariable.md",
			"scheme": "https",
			"authority": "github.com"
		}
	},
	"severity": 4,
	"message": "\"self\" is not defined",
	"source": "Pylance",
	"startLineNumber": 83,
	"startColumn": 16,
	"endLineNumber": 83,
	"endColumn": 20,
	"modelVersionId": 79,
	"origin": "extHost1"
},{
	"resource": "/C:/Users/Nikhat/OneDrive/Documents/GitHub/subscription-billing-engine-asadtalcher-sudo/billing_engine_starter/billing_engine/billing/cycle.py",
	"owner": "Pylance",
	"code": {
		"value": "reportUndefinedVariable",
		"target": {
			"$mid": 1,
			"path": "/microsoft/pylance-release/blob/main/docs/diagnostics/reportUndefinedVariable.md",
			"scheme": "https",
			"authority": "github.com"
		}
	},
	"severity": 4,
	"message": "\"self\" is not defined",
	"source": "Pylance",
	"startLineNumber": 88,
	"startColumn": 20,
	"endLineNumber": 88,
	"endColumn": 24,
	"modelVersionId": 79,
	"origin": "extHost1"
},{
	"resource": "/C:/Users/Nikhat/OneDrive/Documents/GitHub/subscription-billing-engine-asadtalcher-sudo/billing_engine_starter/billing_engine/billing/cycle.py",
	"owner": "Pylance",
	"code": {
		"value": "reportUndefinedVariable",
		"target": {
			"$mid": 1,
			"path": "/microsoft/pylance-release/blob/main/docs/diagnostics/reportUndefinedVariable.md",
			"scheme": "https",
			"authority": "github.com"
		}
	},
	"severity": 4,
	"message": "\"self\" is not defined",
	"source": "Pylance",
	"startLineNumber": 89,
	"startColumn": 20,
	"endLineNumber": 89,
	"endColumn": 24,
	"modelVersionId": 79,
	"origin": "extHost1"
},{
	"resource": "/C:/Users/Nikhat/OneDrive/Documents/GitHub/subscription-billing-engine-asadtalcher-sudo/billing_engine_starter/billing_engine/billing/cycle.py",
	"owner": "Pylance",
	"code": {
		"value": "reportUndefinedVariable",
		"target": {
			"$mid": 1,
			"path": "/microsoft/pylance-release/blob/main/docs/diagnostics/reportUndefinedVariable.md",
			"scheme": "https",
			"authority": "github.com"
		}
	},
	"severity": 4,
	"message": "\"self\" is not defined",
	"source": "Pylance",
	"startLineNumber": 90,
	"startColumn": 33,
	"endLineNumber": 90,
	"endColumn": 37,
	"modelVersionId": 79,
	"origin": "extHost1"
},{
	"resource": "/C:/Users/Nikhat/OneDrive/Documents/GitHub/subscription-billing-engine-asadtalcher-sudo/billing_engine_starter/billing_engine/billing/cycle.py",
	"owner": "Pylance",
	"code": {
		"value": "reportUndefinedVariable",
		"target": {
			"$mid": 1,
			"path": "/microsoft/pylance-release/blob/main/docs/diagnostics/reportUndefinedVariable.md",
			"scheme": "https",
			"authority": "github.com"
		}
	},
	"severity": 4,
	"message": "\"self\" is not defined",
	"source": "Pylance",
	"startLineNumber": 91,
	"startColumn": 32,
	"endLineNumber": 91,
	"endColumn": 36,
	"modelVersionId": 79,
	"origin": "extHost1"
},{
	"resource": "/C:/Users/Nikhat/OneDrive/Documents/GitHub/subscription-billing-engine-asadtalcher-sudo/billing_engine_starter/billing_engine/billing/cycle.py",
	"owner": "Pylance",
	"code": {
		"value": "reportUndefinedVariable",
		"target": {
			"$mid": 1,
			"path": "/microsoft/pylance-release/blob/main/docs/diagnostics/reportUndefinedVariable.md",
			"scheme": "https",
			"authority": "github.com"
		}
	},
	"severity": 4,
	"message": "\"self\" is not defined",
	"source": "Pylance",
	"startLineNumber": 122,
	"startColumn": 29,
	"endLineNumber": 122,
	"endColumn": 33,
	"modelVersionId": 79,
	"origin": "extHost1"
},{
	"resource": "/C:/Users/Nikhat/OneDrive/Documents/GitHub/subscription-billing-engine-asadtalcher-sudo/billing_engine_starter/billing_engine/billing/cycle.py",
	"owner": "Pylance",
	"code": {
		"value": "reportUndefinedVariable",
		"target": {
			"$mid": 1,
			"path": "/microsoft/pylance-release/blob/main/docs/diagnostics/reportUndefinedVariable.md",
			"scheme": "https",
			"authority": "github.com"
		}
	},
	"severity": 4,
	"message": "\"self\" is not defined",
	"source": "Pylance",
	"startLineNumber": 125,
	"startColumn": 17,
	"endLineNumber": 125,
	"endColumn": 21,
	"modelVersionId": 79,
	"origin": "extHost1"
},{
	"resource": "/C:/Users/Nikhat/OneDrive/Documents/GitHub/subscription-billing-engine-asadtalcher-sudo/billing_engine_starter/billing_engine/billing/cycle.py",
	"owner": "Pylance",
	"code": {
		"value": "reportUndefinedVariable",
		"target": {
			"$mid": 1,
			"path": "/microsoft/pylance-release/blob/main/docs/diagnostics/reportUndefinedVariable.md",
			"scheme": "https",
			"authority": "github.com"
		}
	},
	"severity": 4,
	"message": "\"self\" is not defined",
	"source": "Pylance",
	"startLineNumber": 135,
	"startColumn": 13,
	"endLineNumber": 135,
	"endColumn": 17,
	"modelVersionId": 79,
	"origin": "extHost1"
},{
	"resource": "/C:/Users/Nikhat/OneDrive/Documents/GitHub/subscription-billing-engine-asadtalcher-sudo/billing_engine_starter/billing_engine/billing/cycle.py",
	"owner": "Pylance",
	"code": {
		"value": "reportUndefinedVariable",
		"target": {
			"$mid": 1,
			"path": "/microsoft/pylance-release/blob/main/docs/diagnostics/reportUndefinedVariable.md",
			"scheme": "https",
			"authority": "github.com"
		}
	},
	"severity": 4,
	"message": "\"self\" is not defined",
	"source": "Pylance",
	"startLineNumber": 155,
	"startColumn": 13,
	"endLineNumber": 155,
	"endColumn": 17,
	"modelVersionId": 79,
	"origin": "extHost1"
},{
	"resource": "/C:/Users/Nikhat/OneDrive/Documents/GitHub/subscription-billing-engine-asadtalcher-sudo/billing_engine_starter/billing_engine/billing/cycle.py",
	"owner": "Pylance",
	"code": {
		"value": "reportUndefinedVariable",
		"target": {
			"$mid": 1,
			"path": "/microsoft/pylance-release/blob/main/docs/diagnostics/reportUndefinedVariable.md",
			"scheme": "https",
			"authority": "github.com"
		}
	},
	"severity": 4,
	"message": "\"sqlite3\" is not defined",
	"source": "Pylance",
	"startLineNumber": 158,
	"startColumn": 16,
	"endLineNumber": 158,
	"endColumn": 23,
	"modelVersionId": 79,
	"origin": "extHost1"
}]

    # --------------------------------------------------------
    def upgrade_subscription(self, subscription_id: int, new_plan_id: int, switch_date: date) -> None:
        """Mid-cycle upgrade — Day 4 stretch."""
        # TODO Day 4
        raise NotImplementedError("Day 4: implement BillingCycle.upgrade_subscription")
