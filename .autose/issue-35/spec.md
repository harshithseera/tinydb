# Spec: TinyDB.batch() context manager (issue 35)

Source S1: issue text. Requested: `with db.batch():` groups writes into one storage write, with rollback on exception, nesting, and works with any storage including CachingMiddleware.

## Acceptance criteria
AC-1: Given a TinyDB on a storage that counts write calls, When several inserts and updates across the default table and `db.table('logs')` run inside `with db.batch():`, Then storage.write is called exactly once after the block exits (not during it) and all changes are persisted.
AC-2: Given a TinyDB with existing documents, When inside `with db.batch():` a document is inserted and another updated and then `search`/`count`/`get` are called within the block, Then they already reflect those changes.
AC-3: Given a TinyDB with existing documents and a known next doc ID, When an exception is raised inside `with db.batch():` after inserts/updates/removes, Then the exception propagates, storage contents are unchanged with no write, and a subsequent insert gets the same doc ID it would have received had the block never run.
AC-4: Given a TinyDB, When `with db.batch():` is nested inside another `db.batch()`, or a batch makes no changes, Then the inner block does not write, the outer block writes once on exit, and a batch with no changes performs no storage write.
AC-5: Given a TinyDB using `CachingMiddleware(MemoryStorage)`, When a batch runs and exits normally or with an exception, Then committed data is correct on success and unchanged after failure.

## Assumptions
- `batch()` is a method on `TinyDB` (as in the example) and is a context manager; tables from `db.table()` share it.
- "Nothing changed" means no insert/update/remove/truncate mutated data inside the block.
- Rollback restores in-memory table state and per-table next-ID counters.
- Batch need not be thread-safe beyond existing behaviour.
- Exceptions raised in the block propagate unchanged.

## Blocking open questions
None
