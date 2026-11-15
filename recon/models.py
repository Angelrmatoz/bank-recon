"""Core domain types for bank reconciliation."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True, slots=True)
class Transaction:
    """A single bank or ledger movement, with money stored as integer cents."""

    id: int
    date: date
    amount_cents: int
    description: str
    source: str


@dataclass(frozen=True, slots=True)
class Match:
    """A one-to-one match between a bank row and a ledger row."""

    bank_id: int
    ledger_id: int
    date: date
    amount_cents: int
