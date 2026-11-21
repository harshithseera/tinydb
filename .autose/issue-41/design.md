## Approach
Add a `toggle(field)` factory to `tinydb/operations.py`, following the existing pattern: it returns a `Callable[[MutableMapping], None]` that mutates the document in place. The transform reads `doc[field]` (a missing field raises `KeyError` naturally), raises `TypeError` unless `isinstance(value, bool)`, and only then assigns `not value`. Validation happens before assignment, so the document is never partially changed. `Table.update` applies operations inside the `_update_table` updater, so an exception propagates before `write()` is called and nothing is stored (ADR-1, constraint 2). No changes to `Table`, queries or storages are needed. Usage docs get one line in the operations list.

## Files to change
- `tinydb/operations.py` — add `toggle`.
- `tests/test_operations.py` — add tests for toggle (import `toggle`, `pytest`).
- `docs/usage.rst` — add `toggle(key)` to the list of operations (near line 313).

## Functions
- `tinydb/operations.py::toggle` (new) — returns `transform(doc)` that raises `KeyError` if the field is missing, `TypeError` if the value is not a bool, otherwise sets `doc[field] = not doc[field]`.
- `tests/test_operations.py::test_toggle` (new) — AC-1: False->True and True->False via `db.update(toggle('done'))`.
- `tests/test_operations.py::test_toggle_missing_field` (new) — AC-2: `KeyError`, stored docs unchanged.
- `tests/test_operations.py::test_toggle_non_bool` (new) — AC-3/AC-4: parametrized over `1`, `0`, `'yes'`, `None`; `TypeError`, stored doc unchanged.

## Risks
- `bool` is a subclass of `int`, so the check must be `isinstance(value, bool)`; `isinstance(value, int)` would wrongly accept ints.
- If one document in a multi-document update fails, the whole `update` raises before `write()`, so earlier documents in that call are also not persisted. This matches the "nothing written" assumption.
- Query hashing/caching is unaffected: operations are not queries, and `_update_table` still clears the query cache on successful writes.
- The module already defines `set`, which shadows the builtin, so the new code must not use the builtin `set` in `operations.py`.
