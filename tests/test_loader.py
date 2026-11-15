from pathlib import Path

import pytest

from recon.loader import LoaderError, load_csv

FIXTURES = Path(__file__).parent / "fixtures"


def test_loads_valid_rows() -> None:
    result = load_csv(FIXTURES / "bank.csv", "bank")

    assert result.errors == []
    assert [tx.id for tx in result.transactions] == [1, 2, 3, 4]
    assert result.transactions[0].amount_cents == 10_000
    assert result.transactions[1].amount_cents == -2_550
    assert result.transactions[0].date.isoformat() == "2024-01-02"
    assert all(tx.source == "bank" for tx in result.transactions)


def test_invalid_rows_reported_and_skipped() -> None:
    result = load_csv(FIXTURES / "invalid.csv", "bank")

    assert [tx.id for tx in result.transactions] == [1]
    assert len(result.errors) == 5
    assert any("invalid date" in error for error in result.errors)
    assert any("invalid amount" in error for error in result.errors)
    assert any("invalid id" in error for error in result.errors)
    assert any("duplicate id" in error for error in result.errors)


def test_header_only_means_no_rows(tmp_path: Path) -> None:
    path = tmp_path / "empty.csv"
    path.write_text("id,date,amount,description\n", encoding="utf-8")

    result = load_csv(path, "ledger")

    assert result.transactions == []
    assert result.errors == []


def test_missing_columns_is_fatal(tmp_path: Path) -> None:
    path = tmp_path / "bad.csv"
    path.write_text("id,date\n1,2024-01-01\n", encoding="utf-8")

    with pytest.raises(LoaderError, match="amount, description"):
        load_csv(path, "bank")


def test_missing_file_raises_oserror(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        load_csv(tmp_path / "does-not-exist.csv", "bank")
