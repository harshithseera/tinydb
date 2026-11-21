## Approach
Add a new operation factory `append(field, val)` to `tinydb/operations.py`, next to `add`, `set`, etc. It returns a `transform(doc)` closure that `Table.update` applies inside the `updater` run by `Table._update_table`. If `field` is missing it sets `doc[field] = [val]`. If the existing value is a `list` it calls `.append(val)`. Otherwise it raises `TypeError`, which includes a `None` value. The error is raised inside the updater, before `Storage.write()` is called, so the stored data stays unchanged (ADR-1, Constraint 2). No change to `Table`, `Query` or storages is needed. The module only needs the existing imports. A short entry is added to the operations list in `docs/usage.rst`.

## Files to change
- `tinydb/operations.py` — add `append`.
- `tests/test_operations.py` — add tests for append to an existing list, a missing field, a non-list value (raises `TypeError`, data unchanged), and a `None` value.
- `docs/usage.rst` — add `append(key, value)` to the list of update operations (around line 313).

## Functions
- `tinydb/operations.py::append` (new) — `append(field: str, val: Any) -> Callable[[MutableMapping], None]`; the inner `transform` creates `[val]` if `field not in doc`, appends if `isinstance(doc[field], list)`, else raises `TypeError`.
- `tests/test_operations.py::test_append` (new) — AC-1.
- `tests/test_operations.py::test_append_missing_field` (new) — AC-2.
- `tests/test_operations.py::test_append_non_list` (new) — AC-3: `pytest.raises(TypeError)` and the field is still `'abc'` after reading back from the db. It also covers the `None` case.

## Risks
- Query caching and hashing are not affected. `Table._update_table` already clears the query cache after a successful write, and a failed update never reaches the write or the cache clear.
- A list value is appended as a single element, not extended, as the spec says.
- `Table.update` with several matching documents: if one document raises `TypeError`, no write happens, so none of the documents are updated. This is existing behavior for failing operations such as `add`.
- The `set` function in this module shadows the builtin `set`, so `append` must not use `set(...)`.
- `tests/test_operations.py` must import `pytest` if it does not already (its current first import is `tinydb.operations`).
