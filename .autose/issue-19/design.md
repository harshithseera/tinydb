## Approach
Add a new `append(field, value)` factory to `tinydb/operations.py`, following the existing pattern of returning a `transform(doc: MutableMapping)` closure that `Table.update` applies in place. The closure checks whether `field` is in the document. If it is missing, it sets `doc[field] = [value]`. If the value is a `list`, it calls `.append(value)`. Otherwise it raises `TypeError`, which includes an explicit `None` value, tuples and strings. `Table._update_table` runs the updater before it calls `write()`, so an exception leaves the stored data unchanged (AC-3). Only the matching documents are passed to the updater (AC-4). No storage, query or table code changes. Constraint 2 still holds because the write goes through `_update_table`, which clears the query cache.

## Files to change
- `tinydb/operations.py` — add `append`.
- `tests/test_operations.py` — import `append` and add tests for AC-1 to AC-4.
- `docs/usage.rst` — add `append(key, value)` to the list of operations (near line 313).

## Functions
- `tinydb/operations.py::append` (new) — returns a transform that appends `value` as a single element to the list in `doc[field]`, starts a new list `[value]` if the field is missing, and raises `TypeError` if the field exists and is not a `list`.
- `tests/test_operations.py::test_append` (new) — existing list gains the value (AC-1) and a nested list value is appended as one element.
- `tests/test_operations.py::test_append_missing_field` (new) — the field is created as `['urgent']` (AC-2).
- `tests/test_operations.py::test_append_non_list` (new) — `pytest.raises(TypeError)` for a str, and for explicit `None`; the stored value is unchanged afterwards (AC-3).
- `tests/test_operations.py::test_append_only_matching` (new) — only the document matched by the query is changed (AC-4).

## Risks
- In-place mutation of the list. `Table.update` works on the data it has just read and converted, so this is safe. For `MemoryStorage` and `CachingMiddleware`, the read data may be shared with the stored object. The `TypeError` is raised before any mutation, so a partial change cannot happen. In a multi-document update, documents processed before the failing one are not written, because `write()` is never reached.
- Query caching and hashing are unaffected. `append` is an update operation, not a query, and `_update_table` clears the cache after the write.
- `tests/test_operations.py` needs `pytest` imported for `pytest.raises`, if it is not already.
- Name shadowing: `operations.py` already defines `set`, so `append` must not use `set` internally.
