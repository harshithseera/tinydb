# Spec: issue 17 - ordering comparisons on mixed-type fields

## Overview
`Query().f < v`, `<=`, `>`, `>=` raise `TypeError` when a document's value is not comparable with the right-hand side (S1, CONFIRMED). The issue asks that such documents simply not match, like documents with a missing field. Code read: `tinydb/queries.py` `__lt__/__le__/__gt__/__ge__` call the operator directly; only path-resolution errors are caught in `_generate_test`.

## Requirements
- FR-001 (CONFIRMED, S1): For `<`, `<=`, `>`, `>=`, a document whose value is not comparable with the right-hand side shall not match, and no exception shall be raised.
- FR-002 (INFERRED): Comparable values keep their current behaviour.

## Acceptance criteria
AC-1: Given a table with documents price 2, price "TBD" and price 150, When `db.search(Query().price < 10)` is run, Then no exception is raised and only the price 2 document is returned.
AC-2: Given the same table, When `<=`, `>` and `>=` queries with a numeric right-hand side (for example `> 10`, `>= 150`, `<= 2`) are run, Then no exception is raised and the "TBD" document is never returned, while matching numeric documents are returned.
AC-3: Given a table with documents price 2, price 150 and one without a price field, When `Query().price < 10` and `Query().price >= 150` are run, Then only the price 2 document and only the price 150 document are returned respectively.
AC-4: Given a table with a "TBD" price document (item 'lamp') and a numeric price document, When `(Query().price < 10) | (Query().item == 'lamp')` is run, Then no exception is raised and both the numeric document and the lamp document are returned.

## Assumptions
- ASM-1: Only a `TypeError` from the comparison is treated as "no match"; other exceptions still propagate.
- ASM-2: Scope is `<`, `<=`, `>`, `>=` only; `==`/`!=` already work on mixed types.
- ASM-3: Other non-orderable values (`None`, lists, etc.) are treated like "TBD" (no match).
- ASM-4: Negation (`~`) of a skipped comparison behaves as for any non-matching query; not specified by the issue.

## Blocking open questions
None
