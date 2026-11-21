# Spec: datetime support (issue #5)

## Overview
Source S1 (issue): inserting a document containing a `datetime.datetime` into a `TinyDB` with the default JSON storage raises an error (json cannot serialize datetime). The reporter asks whether TinyDB can support dates. Type is "unclear"; the reporter gives no required storage format or API.

Requirement (INFERRED from S1): the default TinyDB usage shall accept `datetime` values in documents and return them as equal `datetime` values when read back, including after the database is reopened from disk.

## Acceptance criteria
AC-1: Given a TinyDB on a new JSON file, When a document `{'title': 'hello', 'created': dt}` with `dt = datetime(2024, 1, 2, 3, 4, 5)` is inserted, Then no exception is raised.
AC-2: Given that document was inserted, When it is read back via `db.all()` or `db.get(...)`, Then `doc['created'] == dt` and `isinstance(doc['created'], datetime)`.
AC-3: Given that document was inserted and the db closed, When a new `TinyDB` is opened on the same file and the document is read, Then `doc['created']` equals `dt` as a `datetime`.
AC-4: Given a document with a datetime field is stored, When `db.search(Query().created == dt)` is run, Then exactly that document is returned.
AC-5: Given documents containing only JSON-native values (str, int, list, nested dict), When inserted and read back, Then they are returned unchanged.

## Assumptions
- Support applies to the default JSON storage via the public API, with no extra configuration required by the user.
- Only `datetime.datetime` is required; `date`/`time` are out of scope unless trivially included.
- Naive datetimes are used in tests; timezone-aware handling is not specified.
- The on-disk representation (e.g. ISO 8601 string) is an implementation choice, provided round trip yields an equal `datetime`.
- Existing stored string values must not be mistakenly converted into datetimes unless they are unambiguously tagged as such (AC-5).

## Blocking open questions
None
