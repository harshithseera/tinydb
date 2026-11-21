# Spec: `toggle` update operation (issue #44)

## Overview
Add `toggle(field)` to `tinydb.operations` that flips a boolean field in place, so callers need not read the document first. Missing or non-bool fields must raise an error rather than be coerced (source: issue text).

## Acceptance criteria
AC-1: Given a table with a document `{'done': False}`, When `db.update(toggle('done'))` is called, Then the document's `done` is `True`, and calling it again makes it `False`.
AC-2: Given a table with several documents with differing `done` values, When `db.update(toggle('done'), where('name') == 'a')` is called, Then only the matching document is flipped and the others are unchanged.
AC-3: Given a document without a `done` field, When `db.update(toggle('done'))` is called, Then an exception is raised and the document is unchanged.
AC-4: Given a document whose `done` is a non-bool value (e.g. `1`, `0`, `'yes'`, `None`), When `db.update(toggle('done'))` is called, Then an exception is raised and the stored value is unchanged.

## Assumptions
- A missing field raises `KeyError` (consistent with `delete`/`add`); a non-bool value raises `TypeError`.
- Integers 0/1 are not treated as bools (strict `isinstance(x, bool)` check).
- A failed update leaves stored data unchanged.
- `toggle` follows the existing operation signature: returns a callable taking the document.

## Blocking open questions
None
