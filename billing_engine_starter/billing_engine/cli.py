"""
CLI entrypoint.

Subcommands to implement (Day 4):
    billing init                              -- create / migrate the DB
    billing customer add <name> <email> <country> [--state CODE]
    billing plan list
    billing subscribe <customer_id> <plan_id> [--trial-days N] [--discount CODE]
    billing bill run [--date YYYY-MM-DD]
    billing invoice show <invoice_id>          -- prints PLAIN TEXT invoice
    billing upgrade <subscription_id> <new_plan_id> [--date YYYY-MM-DD]   (STRETCH)
    billing demo                              -- run the scripted scenario

Use argparse with subparsers. Keep each subcommand handler in its own function.

PDF rendering is OUT OF SCOPE for the core project — `invoice show` should
print a clean PLAIN-TEXT invoice (see helper `format_invoice_text` below).
PDF generation is BONUS: see `billing_engine/pdf/renderer.py`.
"""

from __future__ import annotations

import argparse
import sys
from datetime import date

from billing_engine.db.database import Database
from billing_engine.models import Invoice


def format_invoice_text(invoice: Invoice, customer_name: str, plan_name: str) -> str:
    """Render an invoice as a plain-text receipt. Pure function — easy to test."""
    lines = [
        f"INVOICE #{invoice.id}",
        "=" * 60,
        f"Customer: {customer_name}",
        f"Plan:     {plan_name}",
        f"Period:   {invoice.period_start.isoformat()} to {invoice.period_end.isoformat()}",
        "-" * 60,
    ]

    for item in invoice.line_items:
        sign = "+" if item.amount.amount >= 0 else "-"
        amount = abs(item.amount.amount)
        amount_text = f"{item.amount.currency} {amount:.2f}"
        lines.append(f"{item.description:<42} {sign} {amount_text}")

    lines.extend(
        [
            "-" * 60,
            f"TOTAL     {invoice.total.currency} {invoice.total.amount:.2f}",
            f"Status:   {invoice.status.value}",
        ]
    )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="billing", description="Subscription Billing CLI")
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("init", help="initialize the database")
    sub.add_parser("demo", help="run the demo scenario")
    sub.add_parser(
        "invoice-show",
        help="show a plain-text invoice",
    )

    args = parser.parse_args(argv)

    if args.cmd == "init":
        Database("billing.db").init_schema()
        print("Database initialized.")
        return 0

    if args.cmd == "demo":
        return run_demo()

    if args.cmd == "invoice-show":
        print("invoice-show requires an invoice object in the caller flow.", file=sys.stderr)
        return 2

    print(f"TODO: implement command '{args.cmd}'", file=sys.stderr)
    return 2


def run_demo() -> int:
    """Scripted end-to-end scenario for the `demo` subcommand.

    Should mirror `tests/test_demo_scenario.py::TestEndToEndScenario::test_full_lifecycle`
    and print a human-readable summary to stdout.
    """
    print("Demo scenario is ready to run with the billing engine pipeline.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
