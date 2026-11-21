# Spec: issue 16 - dropped table handle returns stale search() results

## Overview
`Database.drop_table` / `drop_tables` remove table data from storage and forget the Table instances in `db._tables`, but do not clear the query cache (`Table._query_cache`) of handles the user still holds. A held handle's `search()` returns cached documents from before the drop, while `all()`/`len()` correctly show empty.

## Requirements
- FR-1 (CONFIRMED, S1): After `drop_table(name)`, `search()` on a previously obtained handle for that table shall reflect the empty table, including for queries run before the drop.
- FR-2 (CONFIRMED, S1): The same shall hold after `drop_tables()`.

## Acceptance criteria
AC-1: Given a MemoryStorage TinyDB with table 'users' holding {'name': 'ann'} and a held handle on which `search(Query().name == 'ann')` was already run, When `db.drop_table('users')` is called, Then `search(Query().name == 'ann')` on the held handle returns `[]`.
AC-2: Given a MemoryStorage TinyDB with table 'users' holding {'name': 'ann'} and a held handle on which `search(Query().name == 'ann')` was already run, When `db.drop_tables()` is called, Then `search(Query().name == 'ann')` on the held handle returns `[]`.
AC-3: Given a table whose search was cached and then dropped via `drop_table`, When a document {'name': 'bob'} is inserted via the held handle, Then `search(Query().name == 'ann')` returns `[]` and `search(Query().name == 'bob')` returns `[{'name': 'bob'}]`.

## Assumptions
- Held handles remain usable after the drop (as in the issue); no error is raised on them.
- Fix scope is cache invalidation only; behaviour of `all()`, `len()` and dropping non-existent tables is unchanged.

## Blocking open questions
None
