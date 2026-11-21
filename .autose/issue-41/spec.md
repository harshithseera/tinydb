# Spec: `toggle` update operation (issue #41)

## Overview
S1: add `toggle(field)` to `tinydb.operations` that flips a boolean field in place, usable like the existing operations (`db.update(toggle('done'), query)`). The user wants an error, not a guess, when the field is missing or not a bool (firm, CONFIRMED).

## Requirements
- FR-001 (CONFIRMED, S1): `toggle(field)` returns a transform that sets `doc[field]` to `not doc[field]` when it is a bool.
- FR-002 (CONFIRMED, S1): If the field is missing, an exception is raised and the document is unchanged.
- FR-003 (CONFIRMED, S1): If the field exists but is not a bool, an exception is raised and the document is unchanged.

## Acceptance criteria
AC-1: Given a table with documents `{'done': False}` and `{'done': True}`, When `db.update(toggle('done'))` is called, Then the first document has `done` equal to `True` and the second has `done` equal to `False`.
AC-2: Given a document without a `done` field, When `db.update(toggle('done'))` is called, Then a `KeyError` is raised and the stored document is unchanged.
AC-3: Given a document with `done` equal to `1` (an int, not a bool), When `db.update(toggle('done'))` is called, Then a `TypeError` is raised and the stored document still has `done` equal to `1`.
AC-4: Given a document with `done` equal to the string `'yes'` or `None`, When `db.update(toggle('done'))` is called, Then a `TypeError` is raised and the stored document is unchanged.

## Assumptions
- A missing field raises `KeyError`, consistent with `delete`/`increment`; the issue only asks for "an error".
- A non-bool value raises `TypeError`; the issue does not name the type. Ints such as 0/1 count as non-bool (strict `isinstance(value, bool)`).
- Nothing is written to storage when the error is raised.
- Only a single field name is supported; nested paths are out of scope.

## Blocking open questions
None
