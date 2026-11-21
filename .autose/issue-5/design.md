## Approach
Add datetime support inside `JSONStorage` only, keeping the whole-database `read()`/`write()` contract (ADR-1) and the str-key/`None`-for-empty rules unchanged. On write, `json.dumps` gets a `default` hook that encodes a `datetime` as a tagged single-key object `{"$tinydb_datetime": "<isoformat>"}`. On read, `json.load` gets an `object_hook` that turns exactly such a one-key tagged dict back into a `datetime` via `fromisoformat`. Because `Table` reads through the storage, documents come back with real `datetime` values, so `Query().created == dt` compares and hashes datetimes (hashable, so `freeze` and the query cache work unchanged). Plain strings are never converted, only the explicit tag, so JSON-native data is unaffected. User-supplied `default` in kwargs is respected: ours is used only if the user gave none. `Table`, `Query` and `TinyDB` need no changes, so the dependency direction (constraint 5) is preserved.

## Files to change
- `tinydb/storages.py` — add datetime encode/decode helpers and use them in `JSONStorage.read` and `JSONStorage.write`.
- `tests/test_storages.py` — add datetime tests.

## Functions
- `tinydb/storages.py::_encode_default` (new) — `json` `default` hook: returns the tagged dict for `datetime`, otherwise raises `TypeError`.
- `tinydb/storages.py::_decode_hook` (new) — `object_hook`: if the dict has exactly the tag key with a string value, returns `datetime.fromisoformat(value)`; otherwise returns the dict unchanged (invalid value falls back to the dict).
- `tinydb/storages.py::JSONStorage.write` — call `json.dumps(data, **{'default': _encode_default, **self.kwargs})`.
- `tinydb/storages.py::JSONStorage.read` — call `json.load(self._handle, object_hook=_decode_hook)`.
- `tests/test_storages.py::test_json_datetime_roundtrip` (new) — insert, `all()`/`get` equality and type (AC-1, AC-2).
- `tests/test_storages.py::test_json_datetime_reopen` (new) — close and reopen the file, value equal (AC-3).
- `tests/test_storages.py::test_json_datetime_query` (new) — `search(Query().created == dt)` returns the doc (AC-4).
- `tests/test_storages.py::test_json_native_values_unchanged` (new) — str/int/list/nested dict, including a plain ISO-looking string, remain unchanged (AC-5).

## Risks
- A user document that is literally a one-key dict with the tag key would be decoded as a datetime; the tag name is chosen to be unlikely to collide.
- Data files containing datetimes are readable by plain JSON tools only as tagged objects, not as strings; files written by older versions load fine.
- `MemoryStorage` and `CachingMiddleware` over memory keep Python objects, so datetimes already work there; `CachingMiddleware` wrapping `JSONStorage` encodes at flush time, which still goes through `write`.
- Query cache/hashing: datetimes are hashable via `freeze`, so `hashval` is unchanged and caching works. Cached documents hold datetime objects, which are immutable.
- A user-supplied `default` kwarg overrides ours, disabling datetime support in that case. Timezone-aware datetimes round trip through `isoformat`/`fromisoformat` but are untested beyond the naive case; `fromisoformat` needs Python 3.7+.
