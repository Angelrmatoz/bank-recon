# bank-recon

Bank reconciliation engine in Python. Phase 0 loads bank and ledger CSV files
and matches rows one-to-one on exact `(date, amount)`.

Repository: <https://github.com/Angelrmatoz/bank-recon>

## Requirements

- Python 3.10+
- pytest available in the environment

Runtime uses the standard library only.

## Verify

From the repository root:

```console
python -m pytest -q
```

No install step is required: tests import `recon` from the working directory.

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
