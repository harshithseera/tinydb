# Spec: `append` operation for list fields (issue 4)

Source S1: the issue text. Request: add `tinydb.operations.append(field, value)`, usable with `db.update`.

- FR-001 (CONFIRMED, S1): `append(field, val)` adds `val` to the end of the list stored at `field`.
- FR-002 (CONFIRMED, S1): If `field` is missing, it is created as `[val]`.
- FR-003 (CONFIRMED, S1): If `field` exists and is not a list, a `TypeError` is raised and the data is left unchanged.

## Acceptance criteria
AC-1: Given a document `{'id': 3, 'tags': ['a']}`, When `db.update(append('tags', 'urgent'), Query().id == 3)` is called, Then the document's `tags` equals `['a', 'urgent']`.
AC-2: Given a document `{'id': 3}` with no `tags` field, When `db.update(append('tags', 'urgent'), Query().id == 3)` is called, Then the document's `tags` equals `['urgent']`.
AC-3: Given a document `{'id': 3, 'tags': 'abc'}` where `tags` is not a list, When `db.update(append('tags', 'urgent'), Query().id == 3)` is called, Then a `TypeError` is raised and `tags` is still `'abc'`.
AC-4: Given the existing operations (`add`, `increment`, `set`, and so on), When the existing test suite runs, Then all existing tests still pass.

## Assumptions
- `append` has the signature `append(field, val)`, matching the other operations in `tinydb/operations.py`.
- A `None` value at an existing field counts as "exists but not a list", so it raises `TypeError`. The issue does not cover this case.
- Only the list is mutated in place. No copying or deduplication is done, and a list value is appended as a single element.

## Blocking open questions
None
