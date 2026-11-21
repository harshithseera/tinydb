## Approach
The four ordering operators in `Query` build their test lambdas directly as `value < rhs` etc. Wrapping each comparison so that a `TypeError` yields `False` makes incomparable values simply not match, mirroring how missing fields are already skipped. A small private helper in `queries.py` takes an `operator` function and returns the guarded test, so the four methods stay short and consistent. Only the test callable changes; the `hashval` tuples (`'<'`, `self._path`, `rhs`) stay unchanged, so query caching and hashing behave as before. The module dependency direction is unaffected (only the stdlib `operator` module is used, or no import at all if plain lambdas with try/except are used).

## Files to change
- `tinydb/queries.py` — guard `<`, `<=`, `>`, `>=` tests against `TypeError`.
- `tests/test_queries.py` — add tests for AC-1 to AC-4.

## Functions
- `tinydb/queries.py::Query.__lt__` — use guarded test for `value < rhs`.
- `tinydb/queries.py::Query.__le__` — use guarded test for `value <= rhs`.
- `tinydb/queries.py::Query.__gt__` — use guarded test for `value > rhs`.
- `tinydb/queries.py::Query.__ge__` — use guarded test for `value >= rhs`.
- `tinydb/queries.py::_safe_compare` (new) — takes a comparison function and rhs, returns a callable `value -> bool` that returns `False` when the comparison raises `TypeError`.

## Risks
- Only `TypeError` is caught, so other errors in comparisons still propagate.
- `hashval` is unchanged, so there are no query-cache collisions. The guarded lambdas are not part of the hash.
- `~(Query().price < 10)` will now match documents with incomparable values, because the inner test returns `False`. This is unspecified behaviour and is not tested.
- Custom objects whose comparison methods raise `TypeError` internally are now silently treated as non-matching.
