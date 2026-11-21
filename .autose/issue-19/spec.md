# Spec: `append` update operation (issue 19)

Source S1: issue text. Requested: `tinydb.operations.append(field, value)`; missing field starts a new list (CONFIRMED); non-list field raises `TypeError` without overwriting (CONFIRMED).

## Acceptance criteria
AC-1: Given a document whose `tags` field is the list `['a']`, When `db.update(append('tags', 'urgent'), Query().id == 3)` is run, Then the document's `tags` equals `['a', 'urgent']`.
AC-2: Given a document with no `tags` field, When `append('tags', 'urgent')` is applied via `db.update`, Then the document's `tags` equals `['urgent']`.
AC-3: Given a document whose `tags` field is a non-list value (e.g. the string `'x'`), When `append('tags', 'urgent')` is applied via `db.update`, Then a `TypeError` is raised and the stored `tags` value remains `'x'`.
AC-4: Given two documents, only one matching the query and both having list `tags`, When `append` is applied via `db.update` with that query, Then only the matching document's list gains the value.

## Assumptions
- Appends a single value as one element (list.append semantics); a list value is appended as a nested element, not extended.
- Signature is `append(field, value)`, exported from `tinydb.operations`.
- A field explicitly present with value `None` is non-list and raises `TypeError`.
- Tuples and other sequences count as non-list.

## Blocking open questions
None
