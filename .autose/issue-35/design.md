## Approach
Add `TinyDB.batch()`, a context manager that stages all table writes in an in-memory working copy of the whole database and writes it to storage once on a successful exit. Tables keep calling storage only through `_read_table`/`_update_table` (constraint 2). Those two methods are routed through two small new Table hooks, `_read_all` and `_write_all`. Outside a batch the hooks call `self._storage.read()`/`write()`, so behaviour and the `test_read_once` read counts do not change. Inside a batch, `_read_all` returns the working copy, a deepcopy of `storage.read()` taken at batch start. `_write_all` stores the dict and marks it dirty. Searches, counts and gets therefore see uncommitted changes. `_update_table` still clears the query cache on every update, so cache invalidation (ADR-2) holds. On normal exit of the outermost batch, `storage.write(working)` runs once, and only if dirty. This works with any storage, including `CachingMiddleware`, because only the public `read`/`write` are used. On an exception the working copy is discarded and nothing is written. Every table's `_next_id` is restored to its value at batch start (`None` for tables created during the batch) and all query caches are cleared. The exception propagates. A nested `batch()` only increments a depth counter and is part of the outer batch. The batch state is shared by all tables of the database through a reference that `TinyDB.table()` assigns, including to tables created inside the block.

## Files to change
- `tinydb/database.py` — add `batch()`, a private batch-state class, and batch wiring in `table()`.
- `tinydb/table.py` — add the `_batch` attribute and `_read_all`/`_write_all` hooks, and use them in `_read_table` and `_update_table`.
- `tests/test_tinydb.py` — tests for AC-1 to AC-5 (a counting storage, visibility inside the block, rollback with IDs, nesting, an empty batch, `CachingMiddleware(MemoryStorage)`).

## Functions
- `tinydb/database.py::TinyDB.batch` (new) — `@contextmanager`. It enters or exits the batch state. It re-raises exceptions after rollback.
- `tinydb/database.py::_Batch` (new) — holds `depth`, `data`, `dirty` and the `_next_id` snapshot. It has `begin()`, `commit(storage)` and `rollback(tables)`. Only the outermost exit commits or rolls back. An exception in a nested block marks the whole batch failed, so the outer exit rolls back even if the exception is caught in between.
- `tinydb/database.py::TinyDB.__init__` — create `self._batch_state` (an inactive `_Batch`).
- `tinydb/database.py::TinyDB.table` — pass the batch state to newly created tables (`table._batch = self._batch_state`).
- `tinydb/table.py::Table.__init__` — add `self._batch = None`.
- `tinydb/table.py::Table._read_all` (new) — return the batch working copy if a batch is active, else `self._storage.read()`.
- `tinydb/table.py::Table._write_all` (new) — if a batch is active, store the data and set dirty, else `self._storage.write(data)`.
- `tinydb/table.py::Table._read_table` — use `_read_all()` instead of `self._storage.read()`.
- `tinydb/table.py::Table._update_table` — use `_read_all()`/`_write_all()`. The rest is unchanged, including `clear_cache()`.

## Risks
- Query cache: results cached inside the batch could go stale after a rollback. Rollback clears every open table's cache. Query hashing is not touched.
- `_next_id` must be restored on rollback for every table, including tables created in the block. Missing this gives ID gaps (AC-3).
- `Table.__init__` with `persist_empty=True` calls `_update_table` before `_batch` exists. `_batch` must be set before that call, for example with a class-level default `_batch = None`. Tables created inside a batch need the batch state before construction finishes.
- `drop_table`, `drop_tables` and `tables()` read and write storage directly and bypass the batch. Inside a batch they would see uncommitted state or be overwritten at commit. Document this as unsupported inside `batch()`, or route them through the batch state.
- The deepcopy at batch start costs O(database size). This is acceptable because every write is already O(database size) (ADR-1). It is needed so that in-place mutation of documents cannot leak into storage objects such as `MemoryStorage` or `CachingMiddleware` before commit.
- If `storage.write` fails at commit, the exception propagates. The in-memory next-ID counters and caches are then also rolled back.
- Not thread-safe, as stated in the spec.
