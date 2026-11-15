# bank-recon

Bank reconciliation engine in Python. Phase 0 loads bank and ledger CSV files
and matches rows one-to-one on exact `(date, amount)`.

## Requirements

- Python 3.10+
- pytest (development only)

Runtime uses the standard library only.

## Verify

```console
python -m venv .venv
```

Windows:

```console
.venv\Scripts\activate
```

macOS / Linux:

```console
source .venv/bin/activate
```

Then:

```console
python -m pip install -e ".[dev]"
pytest -q
```

## Usage

```console
python -m recon match --bank tests/fixtures/bank.csv --ledger tests/fixtures/ledger.csv --out matches.csv
```

Input CSV columns: `id,date,amount,description`

- `id`: integer, unique within the file
- `date`: ISO date `YYYY-MM-DD`
- `amount`: decimal string with at most 2 places; parsed into integer cents
- `description`: free text

Invalid rows are reported on stderr, skipped, and make the command exit with
code `1`. A valid run still writes the output file.

Output columns: `bank_id,ledger_id,date,amount_cents`, sorted by `bank_id` then
`ledger_id`.

## Exit codes

- `0`: success
- `1`: data error (invalid rows, missing file, unwritable output)
- `2`: invalid command-line usage

## License

MIT
