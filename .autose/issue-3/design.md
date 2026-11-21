## Approach
Add a `Query.between(lower, upper)` method in `tinydb/queries.py`, placed next to `one_of`. It builds the query through `self._generate_test`, as every other query method does. `_generate_test` already resolves the path and returns False for a missing field (FR-2). It also wraps the result in a `QueryInstance`, so `&`, `|` and `~` work with no further change (FR-4). The test is `lower <= value <= upper`, which is inclusive and works for numbers and strings, including ISO date strings (FR-1, FR-3). The comparison is wrapped in `try/except TypeError` that returns False, so incomparable types do not match and do not raise. The existing operators `<=` and `>=` would raise `TypeError` here, so this is a deliberate choice that follows the spec's assumption. The hash is `('between', self._path, freeze(lower), freeze(upper))`. This follows constraint 4, so the query cache keeps different bounds apart. No other module changes, so the dependency direction stays as it is.

## Files to change
- `tinydb/queries.py` — add the `between` method to `Query`.
- `tests/test_queries.py` — add tests for `between`.
- `docs/usage.rst` — optionally add a one-line entry for `between` in the query list, if that list exists.

## Functions
- `tinydb/queries.py::Query.between` (new) — returns `self._generate_test(test, ('between', self._path, freeze(lower), freeze(upper)))`. `test(value)` returns `lower <= value <= upper` and returns False on `TypeError`.
- `tests/test_queries.py::test_between` (new) — covers AC-1: inclusive bounds on integer ages.
- `tests/test_queries.py::test_between_strings_and_missing` (new) — covers AC-2: ISO date strings, a missing field, no exception, and a nested path or `Query()['x']`.
- `tests/test_queries.py::test_between_combinators` (new) — covers AC-3 and AC-4: `|`, `&` and `~`. Also covers the empty result when lower > upper, and the incomparable-type case giving no match.
- `tests/test_queries.py::test_between_hash` (new) — equal arguments give equal hashes. Different bounds give different hashes. Check that the query is usable in a set or dict.

## Risks
- Hashing and caching: if `lower` or `upper` were left out of `hashval`, queries with different bounds would share a query-cache entry (the #637 bug). Both are in the hash and go through `freeze()`. Unhashable bounds are handled by `freeze`.
- Behaviour differs slightly from `>=` and `<=`, which raise `TypeError` on incomparable types. `between` returns no match instead. This is intentional (see the spec assumptions), and it is documented in the docstring.
- With `~`, a document missing the field matches, as with the other query methods.
- `lower <= value <= upper` is a chained comparison. It evaluates `value` against both bounds, and it does not require `lower <= upper`. Nothing matches when lower > upper.
- A user-defined type whose comparison raises something other than `TypeError` would still propagate the exception, as with the other operators.
