## Approach
`TinyDB.drop_table` and `drop_tables` bypass `Table._update_table`, so the query cache (`Table._query_cache`) of handles the user still holds is never cleared. The fix calls `clear_cache()` on the open `Table` instance(s) before they are removed from `self._tables`. This is the smallest change and leaves storage semantics (ADR-1) untouched. The held handle in the issue is the same object as the one in `_tables` (returned by `table()`), so it is covered. Query hashing and caching logic is not changed. The import direction (constraint 5) is preserved because `database.py` only calls an existing public method on `Table`.

## Files to change
- `tinydb/database.py` — clear the query cache of open tables when dropping them.
- `tests/test_tinydb.py` — add regression tests for AC-1, AC-2, AC-3.

## Functions
- `tinydb/database.py::TinyDB.drop_tables` — before `self._tables.clear()`, call `clear_cache()` on each table in `self._tables.values()`.
- `tinydb/database.py::TinyDB.drop_table` — when `name in self._tables`, call `clear_cache()` on that table before `del`. This happens before the early returns for missing data or a missing table.

## Risks
- A handle not in `_tables` (for example one left over from an earlier drop, or a second `Table` object created directly) keeps its stale cache. This is the known limitation already listed in ADR-2.
- Clearing a cache only drops memoised results, so there is no effect on query hashing or `is_cacheable`.
- Dropping a non-existent table must remain a no-op; `clear_cache()` is only called when the table is in `_tables`.
