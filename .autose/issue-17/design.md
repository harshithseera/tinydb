## Approach
Add a small private helper in `queries.py` that runs an ordering comparison and returns `False` when it raises `TypeError`. `__lt__`, `__le__`, `__gt__` and `__ge__` use it in the lambda they pass to `_generate_test`. Only the test lambda changes. The `hashval` tuples, path resolution and cacheability stay as they are, so the stable-hash and query-cache rules (ADR-2, constraint 4) are untouched. Other exceptions still propagate (ASM-1). `queries.py` gains no new imports, so the module dependency direction (constraint 5) is unchanged. The change is local to `Query` and needs no change to `Table` or the storages.

## Files to change
- `tinydb/queries.py` — add the safe-compare helper and use it in the four ordering operators.
- `tests/test_queries.py` — add tests for mixed-type comparisons.

## Functions
- `tinydb/queries.py::Query.__lt__` — the test lambda calls the helper with `operator.lt` instead of `value < rhs`.
- `tinydb/queries.py::Query.__le__` — same, with `operator.le`.
- `tinydb/queries.py::Query.__gt__` — same, with `operator.gt`.
- `tinydb/queries.py::Query.__ge__` — same, with `operator.ge`.
- `tinydb/queries.py::_ordering_test` (new) — module-level helper `(op, value, rhs) -> bool`. It returns `op(value, rhs)` and returns `False` on `TypeError`. It needs `import operator`, or the four lambdas can use a try/except inline instead.
- `tests/test_queries.py::test_ordering_mixed_types` (new) — covers AC-1 and AC-2 on a table with 2, "TBD" and 150, and also checks `None` and list values.
- `tests/test_queries.py::test_ordering_missing_field` (new) — covers AC-3.
- `tests/test_queries.py::test_ordering_mixed_types_or` (new) — covers AC-4 with `|`.

## Risks
- Catching `TypeError` also hides a `TypeError` raised inside a custom `__lt__` on user types. It is treated as "no match", which is accepted under ASM-1.
- `hashval` is unchanged, so cache keys are the same as before. A query that used to raise was never cached, and one that now returns a result is cached like any other. There is no collision risk.
- `~(Query().price < 10)` now matches the "TBD" document, because negation inverts the `False`. ASM-4 leaves this unspecified. Add a short docstring note.
- Python 3 `str` vs `int` raises `TypeError`, so the behaviour for comparable values does not change (FR-002).
