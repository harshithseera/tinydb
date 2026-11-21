## Approach
Each operation in `tinydb/operations.py` keeps its signature shape but its `field` argument becomes `Union[str, Sequence]`. Small private helpers handle the path logic: a str is always one top-level key (never split on dots), while a tuple/list is walked key by key. The parent mapping is resolved before any mutation, so a `TypeError` for a non-mapping intermediate leaves the document untouched. `set` validates the whole path first and only then creates missing dicts and assigns; the other operations use plain lookups, so a missing key raises `KeyError` as today. Only `operations.py` changes. Storage, `Table._update_table` and query hashing are unaffected, because operations run in place inside the updater closure and the cache is cleared by the existing write path.

## Files to change
- `tinydb/operations.py` — add path helpers; widen type hints; route all six operations through them.
- `tests/test_operations.py` — add tests for nested paths (AC-1 to AC-5).
- `docs/usage.rst` — optional short note on path support near the operations section (~line 306).

## Functions
- `tinydb/operations.py::_split_path` (new) — return `(parent_keys, last_key)` for a str (`([], field)`) or tuple/list; no dot splitting.
- `tinydb/operations.py::_get_parent` (new) — walk `parent_keys` through `doc` with `[]` lookups (KeyError on missing); raise `TypeError` if an intermediate is not a `MutableMapping`; return the parent mapping.
- `tinydb/operations.py::_ensure_parent` (new) — for `set`: first check existing intermediates are MutableMappings (TypeError, stopping at the first missing key), then create missing dicts and return the parent.
- `tinydb/operations.py::delete` — `del parent[last]` via `_get_parent`.
- `tinydb/operations.py::add` — `parent[last] += n` via `_get_parent`.
- `tinydb/operations.py::subtract` — same, with `-=`.
- `tinydb/operations.py::set` — use `_ensure_parent`, then `parent[last] = val`.
- `tinydb/operations.py::increment` — `parent[last] += 1` via `_get_parent`.
- `tinydb/operations.py::decrement` — `parent[last] -= 1` via `_get_parent`.

## Risks
- Str behavior must stay identical (including dotted keys and the `KeyError` for a missing top-level field); a str resolves to an empty parent chain, so the parent is the doc itself.
- Atomicity: for `set`, validation must precede creation of intermediate dicts, or a `TypeError` could leave a half-created structure. For the other operations the parent is resolved before the in-place update, so a failure leaves nothing changed.
- `Document` is a dict subclass, so it passes the `MutableMapping` check, as do nested plain dicts.
- No query hashing or cache impact: `_update_table` clears the query cache after every update, and operations are not hashed.
- An empty path is unspecified; it may raise `IndexError` or `KeyError`. Do not rely on it.
- The module's own `set` shadows the builtin, so the helpers must not use the builtin `set`.
