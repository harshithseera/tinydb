## Approach
The previous attempt changed no library code, so its tests passed on master. This attempt removes a real, measurable inefficiency: `Table.update`, `update_multiple`, and `remove` by query or `doc_ids` always rewrite the whole database via `_update_table`, even when nothing matched. With `JSONStorage` that is a full serialize plus `fsync` of the database for a no-op, which hurts large databases. `_update_table` gets a small opt-out: if the updater returns `False`, it skips `write()` and the cache clear, because nothing changed. Existing updaters return `None`, so their behaviour is unchanged. The updaters of `update` (query and `doc_ids` branches), `update_multiple`, and `remove` (query and `doc_ids` branches) return `False` when they changed no document. This fits ADR-1 and constraint 2: all changes still go through `_update_table`, and the storage interface and the whole-database read/write model stay as they are. The query cache stays valid because the data did not change. Upsert benefits too, since its failed `update` no longer writes before the `insert`.

## Files to change
- `tinydb/table.py` — `_update_table` skips the write and the cache clear when the updater returns `False`. The no-match paths of `update`, `update_multiple`, and `remove` return `False`.
- `tests/test_tables.py` — tests that count storage writes with a counting `MemoryStorage` subclass.

## Functions
- `tinydb/table.py::Table._update_table` — capture the updater's return value. If it `is False`, return before converting the keys back, writing, and calling `clear_cache()`. Update the docstring.
- `tinydb/table.py::Table.update` — in the `cond` and `doc_ids` branches, the updater returns `False` when no document was updated. The unconditional branch may also return `False` when the table is empty.
- `tinydb/table.py::Table.update_multiple` — the updater returns `False` when no document matched.
- `tinydb/table.py::Table.remove` — in the `cond` and `doc_ids` branches, the updater returns `False` when nothing was removed.
- `tests/test_tables.py::test_update_no_match_does_not_write` (new) — 1000 documents, `update({'x': 1}, where('n') > 5000)` gives 0 writes and an empty result.
- `tests/test_tables.py::test_remove_no_match_does_not_write` (new) — the same check for `remove(cond)` and for `remove(doc_ids=[999999])`.
- `tests/test_tables.py::test_update_match_single_write` (new) — a matching update does exactly 1 write, and the results are correct.
- `tests/test_tables.py::test_noop_write_keeps_query_cache` (new) — after a no-op update, a repeated `search` does 0 storage reads, so the cache is kept.
- `tests/test_tables.py::test_update_after_cached_search_not_stale` (new) — a real update or remove invalidates the cache, and the next search shows the change.

## Risks
- An updater that returns `False` by accident would silently skip a write. Only the explicit `return False` paths do this, and the check is `is False`, so `None` and other values are unaffected.
- The query cache is not cleared on a skipped write. That is correct only because nothing changed. A partly applied updater must never return `False`, and the `doc_ids` updater filters IDs before it changes anything.
- `test_read_once` (`tests/test_storages.py:158`) counts reads, not writes, and no read count changes. `CachingMiddleware` now sees fewer writes for no-op calls. That is harmless, but the existing middleware tests must still pass.
- `perform_update` mutates documents in place. The updater returns `False` only when it did not call it, so no mutation is lost.
- Query hashing is untouched, so constraint 4 is not affected.
