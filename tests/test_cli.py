import csv
from pathlib import Path

from recon.cli import main

FIXTURES = Path(__file__).parent / "fixtures"


def test_cli_writes_sorted_matches(tmp_path: Path, capsys) -> None:
    out = tmp_path / "matches.csv"

    code = main(
        [
            "match",
            "--bank",
            str(FIXTURES / "bank.csv"),
            "--ledger",
            str(FIXTURES / "ledger.csv"),
            "--out",
            str(out),
        ]
    )

    assert code == 0
    with out.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    assert [(row["bank_id"], row["ledger_id"]) for row in rows] == [
        ("1", "10"),
        ("2", "11"),
        ("4", "12"),
    ]
    assert "matched: 3" in capsys.readouterr().out


def test_cli_reports_invalid_rows_and_exits_1(tmp_path: Path, capsys) -> None:
    empty_ledger = tmp_path / "empty-ledger.csv"
    empty_ledger.write_text("id,date,amount,description\n", encoding="utf-8")
    out = tmp_path / "matches.csv"

    code = main(
        [
            "match",
            "--bank",
            str(FIXTURES / "invalid.csv"),
            "--ledger",
            str(empty_ledger),
            "--out",
            str(out),
        ]
    )

    assert code == 1
    captured = capsys.readouterr()
    assert "invalid date" in captured.err
    assert "matched: 0" in captured.out
    assert out.exists()


def test_cli_missing_file_exits_1_without_output(tmp_path: Path, capsys) -> None:
    out = tmp_path / "matches.csv"

    code = main(
        [
            "match",
            "--bank",
            str(tmp_path / "missing.csv"),
            "--ledger",
            str(FIXTURES / "ledger.csv"),
            "--out",
            str(out),
        ]
    )

    assert code == 1
    assert "error:" in capsys.readouterr().err
    assert not out.exists()
