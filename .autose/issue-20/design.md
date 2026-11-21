## Approach
`JSONStorage` is the only place where documents are serialized to JSON, so date support goes there and nothing above it changes (ADR-1, Constraint 1: `read()`/`write()` keep their whole-database contract). `write` passes a `default` hook to `json.dumps` that encodes `datetime.datetime` and `datetime.date` as a tagged dict, e.g. `{"__tinydb_type__": "datetime", "value": "<isoformat>"}`. `read` passes an `object_hook` to `json.load` that turns exactly such tagged dicts back into the original types. The tag keeps a datetime distinguishable from an ISO-looking `str`, so plain strings stay strings (AC-4). A user-supplied `default` in kwargs still wins. Table, Query and the cache are untouched. After reload, documents hold real date objects, so `Query().created == dt` works through normal comparison (AC-3). Files without tagged dicts load exactly as before. Timezone-aware datetimes round-trip via `isoformat`/`fromisoformat`.

## Files to change
- `tinydb/storages.py` — add encode/decode helpers and wire them into `JSONStorage.read` and `JSONStorage.write`.
- `tests/test_storages.py` — add tests for date round-trip, ISO string unchanged, query after reopen.

## Functions
- `tinydb/storages.py::_json_default` (new) — `default` hook for `json.dumps`. Checks `datetime.datetime` first (it subclasses `date`), then `date`. Returns the tagged dict. Raises `TypeError` for anything else.
- `tinydb/storages.py::_json_object_hook` (new) — `object_hook` for `json.load`. If a dict has exactly the tag and value keys and a known type, returns the parsed `datetime`/`date`. Otherwise returns the dict unchanged (also when parsing fails).
- `tinydb/storages.py::JSONStorage.write` — call `json.dumps(data, **{'default': _json_default, **self.kwargs})`.
- `tinydb/storages.py::JSONStorage.read` — call `json.load(self._handle, object_hook=_json_object_hook)`.
- `tests/test_storages.py::test_json_datetime_roundtrip` (new) — AC-1 and AC-2: insert, close, reopen, check values and types.
- `tests/test_storages.py::test_json_datetime_query` (new) — AC-3: search by datetime after reopen.
- `tests/test_storages.py::test_json_iso_string_stays_str` (new) — AC-4.

## Risks
- A user dict that already has the tag keys would be decoded as a date. The namespaced tag, exact key-set check and fall-back on parse failure reduce this.
- Query cache and hashing: unaffected. `freeze` leaves datetimes as they are, and they are hashable. Writes still go through `_update_table`, so cache invalidation is unchanged.
- A user-supplied `default` in kwargs overrides ours, so dates are not encoded in that case; document this in the docstring.
- Files written with dates contain tagged dicts that older TinyDB versions read as plain dicts.
- `MemoryStorage` and `CachingMiddleware` hold raw Python objects and are unaffected. The cached data is only serialized when it is flushed to `JSONStorage`.
