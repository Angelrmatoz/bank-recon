"""Command line interface: python -m recon match ..."""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

from recon.exact import match_exact
from recon.loader import LoaderError, load_csv
from recon.models import Match

EXIT_OK = 0
EXIT_DATA_ERROR = 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="recon")
    subparsers = parser.add_subparsers(dest="command", required=True)

    match = subparsers.add_parser("match", help="match bank rows against ledger rows")
    match.add_argument("--bank", required=True, help="bank statement CSV")
    match.add_argument("--ledger", required=True, help="internal ledger CSV")
    match.add_argument("--out", required=True, help="output matches CSV")
    return parser


def _write_matches(path: Path, matches: list[Match]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["bank_id", "ledger_id", "date", "amount_cents"])
        for match in matches:
            writer.writerow(
                [match.bank_id, match.ledger_id, match.date.isoformat(), match.amount_cents]
            )


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    try:
        bank = load_csv(args.bank, "bank")
        ledger = load_csv(args.ledger, "ledger")
    except (OSError, LoaderError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return EXIT_DATA_ERROR

    errors = bank.errors + ledger.errors
    for error in errors:
        print(f"warning: {error}", file=sys.stderr)

    matches = match_exact(bank.transactions, ledger.transactions)
    try:
        _write_matches(Path(args.out), matches)
    except OSError as exc:
        print(f"error: cannot write {args.out}: {exc}", file=sys.stderr)
        return EXIT_DATA_ERROR

    print(f"bank rows: {len(bank.transactions)} ({len(bank.errors)} invalid)")
    print(f"ledger rows: {len(ledger.transactions)} ({len(ledger.errors)} invalid)")
    print(f"matched: {len(matches)}")
    print(f"unmatched bank rows: {len(bank.transactions) - len(matches)}")
    print(f"output: {args.out}")
    return EXIT_DATA_ERROR if errors else EXIT_OK


if __name__ == "__main__":
    raise SystemExit(main())
