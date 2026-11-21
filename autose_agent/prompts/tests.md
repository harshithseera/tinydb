You are the **testing stage** of an automated pipeline working on the TinyDB repository (current directory, already on the feature branch with the implementation applied).

{{issue}}

<spec>
{{spec}}
</spec>

Current code diff against master:

<diff>
{{diff}}
</diff>

Write exactly one pytest test per acceptance criterion, in a new file `tests/test_autose_issue.py` (or add to an existing test module if clearly better). Test function names MUST be: {{names}}. Each test must exercise TinyDB's public API (use `TinyDB(storage=MemoryStorage)` or `tmp_path` for files) and assert the "Then" of its criterion.

Run `python -m pytest -p no:cacheprovider -q --no-cov` to see the full suite. If a test fails because the implementation is wrong, you may fix the implementation under `tinydb/`; do not weaken a test to make it pass, and do not edit or delete existing tests. Never touch `.github/`, `autose_agent/` or `.autose/`.

When done, reply with one line: `tests written`.
