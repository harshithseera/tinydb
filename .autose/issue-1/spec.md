# Spec: search results must not alias cached documents

## Overview
`Table.search` returns a list copy whose Document objects are shared with the query cache (table.py ~L249-295). Mutating a returned document changes later cached search results. Source S1 (issue): firm expectation that search results are the caller's own copy and the DB changes only via `update`. Status: CONFIRMED.

## Requirements
- FR-001 (CONFIRMED, S1): Mutating a document returned by `search` shall not affect the results of later `search` calls for the same query, nor `all()`.
- FR-002 (INFERRED): The same holds when the result came from the cache (second and later calls).

## Acceptance criteria
AC-1: Given a MemoryStorage TinyDB containing {'name': 'theme', 'value': 'light'}, When a user searches name == 'theme', sets result[0]['value'] = 'dark', and searches again with the same query, Then the second result is [{'name': 'theme', 'value': 'light'}].
AC-2: Given the same database, When a user mutates a document returned by a search and then calls db.all(), Then all() returns the document with value 'light'.
AC-3: Given a query already searched twice, When a user mutates a document from the second result and searches a third time, Then the third result still has value 'light' and its documents are distinct objects from those of the second result.
AC-4: Given a locally mutated search result, When the user calls db.update({'value': 'dark'}, query) and searches again, Then the result has value 'dark' (update still persists changes).

## Assumptions
- The fix applies to table-level search (cache path); copying on return vs. on cache store is an implementation choice.
- Scope is `search`; other read methods are unchanged unless they share the same aliasing.
- doc_id of returned documents is preserved.

## Blocking open questions
None
