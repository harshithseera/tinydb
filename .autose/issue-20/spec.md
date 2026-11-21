# Spec: date/datetime support (issue 20)

Source S1: "Most of my records have a date or timestamp ... TinyDB ... errors when I try to save them ... Any chance TinyDB could handle dates properly?"

- FR-001 (CONFIRMED, S1): Documents containing `datetime.datetime` / `datetime.date` values can be saved to a JSON db file without error.
- FR-002 (INFERRED from "without converting back and forth by hand"): Values read back have the original types.
- Out of scope: other types (Decimal, UUID, etc.), non-JSON storages (MemoryStorage already holds Python objects).

## Acceptance criteria
AC-1: Given a TinyDB on a JSON file with default settings, When a document containing a `datetime.datetime` and a `datetime.date` field is inserted, Then no exception is raised and the file is written.
AC-2: Given a document with datetime and date fields was inserted, When the db is closed, reopened from the same file and the document is fetched via `all()`, Then the fields equal the original values and have types `datetime.datetime` and `datetime.date` respectively.
AC-3: Given stored documents with datetime fields, When `db.search(Query().created == some_datetime)` is run after reopening the file, Then the matching document is returned.
AC-4: Given a document with only plain str/int/list/dict values, When it is stored and reloaded, Then it is unchanged (including a string that looks like an ISO date remains a `str`).

## Assumptions
- Support works with default `JSONStorage` settings, with no user configuration required.
- Round-trip must preserve type, so a datetime is distinguishable from an ISO-formatted string on reload.
- Naive datetimes are required; timezone-aware ones should round-trip too if feasible but are not tested.
- Existing db files without dates continue to load unchanged.

## Blocking open questions
None
