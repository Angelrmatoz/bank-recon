"""Exact one-to-one matching by (date, amount_cents)."""

from __future__ import annotations

from collections import defaultdict, deque
from datetime import date

from recon.models import Match, Transaction


def match_exact(
    bank: list[Transaction], ledger: list[Transaction]
) -> list[Match]:
    """Match bank rows to ledger rows on identical date and amount.

    Each ledger row is consumed at most once. When several ledger rows share
    the same key, the one with the lowest id wins. Output is sorted by
    (bank_id, ledger_id).
    """
    by_key: dict[tuple[date, int], deque[Transaction]] = defaultdict(deque)
    for transaction in sorted(ledger, key=lambda item: item.id):
        by_key[(transaction.date, transaction.amount_cents)].append(transaction)

    matches: list[Match] = []
    for transaction in sorted(bank, key=lambda item: item.id):
        candidates = by_key.get((transaction.date, transaction.amount_cents))
        if not candidates:
            continue
        other = candidates.popleft()
        matches.append(
            Match(
                bank_id=transaction.id,
                ledger_id=other.id,
                date=transaction.date,
                amount_cents=transaction.amount_cents,
            )
        )

    return matches
