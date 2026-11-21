# Spec: Table.count() without a query (issue #46)

Source S1: the issue. Currently `Table.count(cond)` requires `cond` (tinydb/table.py:709) and raises TypeError when it is omitted. The stakeholder firmly asks that `count()` with no query return the total number of documents, and that passing a query behave as it does today.

## Acceptance criteria
AC-1: Given a table with 3 documents, When `table.count()` is called with no arguments, Then it returns 3.
AC-2: Given an empty table, When `table.count()` is called with no arguments, Then it returns 0.
AC-3: Given a table with documents where some match a query, When `table.count(query)` is called, Then it returns the number of matching documents only (unchanged behaviour).
AC-4: Given a table with documents, When `table.count()` is called with no arguments, Then the result equals `len(table)`.

## Assumptions
- Only `Table.count` is in scope. The `TinyDB` default-table proxy delegates attribute access to the table, so it gets the same behaviour.
- "No query" means the argument is omitted. Whether an explicit `None` is accepted is not specified, so it is not tested.
- No change to the return type (int) or to the query cache behaviour.

## Blocking open questions
None
