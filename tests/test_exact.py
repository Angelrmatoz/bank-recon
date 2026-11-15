from datetime import date
from pathlib import Path

from recon.exact import match_exact
from recon.loader import load_csv
from recon.models import Transaction

FIXTURES = Path(__file__).parent / "fixtures"


def load_fixtures():
    bank = load_csv(FIXTURES / "bank.csv", "bank").transactions
    ledger = load_csv(FIXTURES / "ledger.csv", "ledger").transactions
    return bank, ledger


def test_matches_exact_date_and_amount_one_to_one() -> None:
    bank, ledger = load_fixtures()

    matches = match_exact(bank, ledger)

    assert [(m.bank_id, m.ledger_id) for m in matches] == [(1, 10), (2, 11), (4, 12)]


def test_lowest_ledger_id_wins_when_duplicates_exist() -> None:
    bank, ledger = load_fixtures()

    matches = match_exact(bank, ledger)

    assert 13 not in [m.ledger_id for m in matches]


def test_input_order_does_not_change_result() -> None:
    bank, ledger = load_fixtures()

    forward = match_exact(bank, ledger)
    backward = match_exact(list(reversed(bank)), list(reversed(ledger)))

    assert forward == backward


def test_each_ledger_row_is_consumed_once() -> None:
    day = date(2024, 1, 1)
    bank = [
        Transaction(1, day, 500, "first", "bank"),
        Transaction(2, day, 500, "second", "bank"),
    ]
    ledger = [
        Transaction(10, day, 500, "a", "ledger"),
        Transaction(11, day, 500, "b", "ledger"),
    ]

    matches = match_exact(bank, ledger)

    assert [(m.bank_id, m.ledger_id) for m in matches] == [(1, 10), (2, 11)]


def test_no_candidates_returns_empty() -> None:
    day = date(2024, 1, 1)
    bank = [Transaction(1, day, 500, "bank", "bank")]
    ledger = [Transaction(10, date(2024, 1, 2), 500, "different day", "ledger")]

    assert match_exact(bank, ledger) == []


def test_amount_sign_must_match() -> None:
    day = date(2024, 1, 1)
    bank = [Transaction(1, day, -500, "charge", "bank")]
    ledger = [Transaction(10, day, 500, "credit", "ledger")]

    assert match_exact(bank, ledger) == []
