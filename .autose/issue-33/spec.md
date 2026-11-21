# Spec: issue 33 - TinyDB gets slow on large databases

## Overview
Source S1 (issue): a grown database feels sluggish, especially for search and update; asks what can be done. No figures, size, storage type or version given (OPEN, see assumptions). Scope is limited to reducing redundant storage I/O in Table search/update paths, observable through the public API with an instrumented Storage. No architectural change is stated.

## Acceptance criteria
AC-1: Given a table on a counting in-memory Storage holding 1000 documents, When `update({'x': 1}, where('n') > 10)` is called and matches many documents, Then the storage performs exactly one write for the call and every matching document has `x == 1`.
AC-2: Given a table on a counting Storage holding 1000 documents, When `search(where('n') == 5)` is called twice in a row with no writes between, Then the second call performs no storage reads and returns the same documents as the first.
AC-3: Given a table on a counting Storage, When `insert_multiple` is called with 500 documents, Then the storage performs exactly one write and `len(table)` increases by 500.
AC-4: Given a table with a cached search result, When a document is updated or removed and the same query is searched again, Then the result reflects the change (no stale cached data).

## Assumptions
- The issue gives no target; "faster" is interpreted as fewer redundant storage reads/writes per operation, since I/O count is deterministic and testable (wall-clock timing is not).
- Existing behaviour and public API must remain unchanged; results must be identical.
- Where current behaviour already meets an AC (e.g. single write per bulk call, query cache), the AC acts as a regression guard.
- Default JSONStorage and the Table query cache are the relevant paths; no new dependencies or index structures are assumed.

## Blocking open questions
None
