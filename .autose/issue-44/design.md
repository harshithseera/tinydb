## Approach
Add a `toggle(field)` factory to `tinydb/operations.py`, following the existing pattern: it returns a `transform(doc)` closure that `Table.update` applies in place inside `_update_table` (constraint 2). The closure reads `doc[field]`, which raises `KeyError` if the field is missing. It raises `TypeError` unless `type(value) is bool` (a strict check, so `0` and `1` are rejected). Only then does it write `doc[field] = not value`. It validates before it mutates, so the failing document is never changed. If the closure raises, `_update_table` never reaches `write()`, so nothing is persisted and the query cache is not cleared. No change to `Table`, `Query`, or storages is needed, and the module dependency direction is untouched. The new operation also gets a short mention in the docs.

## Files to change
- `tinydb/operations.py` — add `toggle`.
- `tests/test_operations.py` — add tests for AC-1 to AC-4.
- `docs/usage.rst` — add `toggle` to the list of update operations, if such a list exists near line 306.

## Functions
- `tinydb/operations.py::toggle` (new) — `toggle(field: str) -> Callable[[MutableMapping], None]`. The `transform` closure raises `KeyError` if the field is missing and `TypeError` if the value is not a `bool`. Otherwise it sets `doc[field] = not doc[field]`.
- `tests/test_operations.py::test_toggle` (new) — flips `False` to `True` and back (AC-1).
- `tests/test_operations.py::test_toggle_with_query` (new) — with a `where('name') == 'a'` query, only the matching document changes (AC-2).
- `tests/test_operations.py::test_toggle_missing_field` (new) — `pytest.raises(KeyError)`, and the stored data is unchanged (AC-3).
- `tests/test_operations.py::test_toggle_non_bool` (new) — parametrized over `1`, `0`, `'yes'`, `None`. It expects `TypeError` and checks that the stored value is unchanged (AC-4).

## Risks
- Atomicity across several documents: if the toggle fails on a later document, earlier documents in the same `update` call may already be mutated in place. With `MemoryStorage` or `CachingMiddleware`, `read()` can return the live dict, so a partial change could persist even though `write()` is never called. This matches `add`, `increment`, and the other operations. The tests only assert unchanged data for single-document failures. If the tests show a problem, assert on the failing document only.
- Query cache and hashing: there is no impact. Operations are not queries and have no `hashval`. A successful update still goes through `_update_table`, which clears the cache. A failed update leaves the cache as it was, and the data is not written, so the cache is still valid.
- `bool` is a subclass of `int`, so the check must use `type(value) is bool` or `isinstance(value, bool)`. Neither accepts plain ints. numpy bools are rejected, which is acceptable.
- The module shadows the builtin name `set` (an existing `set` function). `toggle` must not use `set(...)`.
