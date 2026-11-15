"""CSV loading and validation.

Money is parsed from decimal strings into integer cents. Invalid rows are
reported and skipped; a malformed header aborts the load.
"""

from __future__ import annotations

import csv
import re
from dataclasses import dataclass
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path

from recon.models import Transaction

REQUIRED_COLUMNS = ("id", "date", "amount", "description")
_AMOUNT_RE = re.compile(r"^[+-]?\d+(?:\.\d{1,2})?$")


class LoaderError(Exception):
    """Fatal problem with the file itself (missing columns, unreadable file)."""


@dataclass(slots=True)
class LoadResult:
    transactions: list[Transaction]
    errors: list[str]


def _parse_amount(raw: str) -> int:
    text = raw.strip()
    if not _AMOUNT_RE.fullmatch(text):
        raise ValueError(f"invalid amount {raw!r}; use a decimal with at most 2 places")
    try:
        value = Decimal(text)
    except InvalidOperation as exc:
        raise ValueError(f"invalid amount {raw!r}") from exc
    return int(value * 100)


def _parse_row(row: dict[str, str], source: str) -> Transaction:
    raw_id = (row.get("id") or "").strip()
    try:
        tx_id = int(raw_id)
    except ValueError as exc:
        raise ValueError(f"invalid id {raw_id!r}") from exc

    raw_date = (row.get("date") or "").strip()
    try:
        tx_date = date.fromisoformat(raw_date)
    except ValueError as exc:
        raise ValueError(f"invalid date {raw_date!r}; expected YYYY-MM-DD") from exc

    amount_cents = _parse_amount(row.get("amount") or "")
    description = (row.get("description") or "").strip()
    return Transaction(tx_id, tx_date, amount_cents, description, source)


def load_csv(path: str | Path, source: str) -> LoadResult:
    """Load a CSV file, skipping and reporting invalid data rows.

    Raises LoaderError when the header is missing required columns.
    """
    path = Path(path)
    transactions: list[Transaction] = []
    errors: list[str] = []
    seen_ids: set[int] = set()

    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        fieldnames = reader.fieldnames or []
        missing = [name for name in REQUIRED_COLUMNS if name not in fieldnames]
        if missing:
            raise LoaderError(
                f"{path}: missing required column(s): {', '.join(missing)}"
            )

        for row in reader:
            line = reader.line_num
            try:
                transaction = _parse_row(row, source)
                if transaction.id in seen_ids:
                    raise ValueError(f"duplicate id {transaction.id}")
            except ValueError as exc:
                errors.append(f"{path}:{line}: {exc}; row skipped")
                continue
            seen_ids.add(transaction.id)
            transactions.append(transaction)

    return LoadResult(transactions, errors)
