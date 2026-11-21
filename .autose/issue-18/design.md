## Approach
Add a single `Query.between(low, high)` method in `tinydb/queries.py`, next to the other comparison operators. It uses `_generate_test`, so path resolution already makes documents without the field not match (KeyError is caught there). The test function evaluates `low <= value <= high` and catches `TypeError` itself, because `_generate_test` only guards path resolution and a plain comparison of a str with an int would raise, while AC-4 requires no exception. The hashval is `('between', self._path, freeze(low), freeze(high))`, so the query is hashable, composable with `&`/`|`/`~`, and cacheable like the others; `_generate_test` also handles `is_cacheable()`. No other module changes, so the dependency direction (constraint 5) and the `Table._update_table` write path are untouched. Docs get one row in the query table.

## Files to change
- `tinydb/queries.py` — add `Query.between`.
- `tests/test_queries.py` — tests for the new method.
- `docs/usage.rst` — add a row to the queries table near line 224.

## Functions
- `tinydb/queries.py::Query.between` (new) — returns `self._generate_test(test, ('between', self._path, freeze(low), freeze(high)))`, where `test(value)` returns `low <= value <= high` and returns False on `TypeError`.
- `tests/test_queries.py::test_between` (new) — AC-1 (inclusive ints 17/18/25/30/31), AC-2 (ISO date strings), AC-3 (missing field), AC-4 (string 'x' against int bounds), low > high matches nothing, and composition with `&` and `~`.
- `tests/test_queries.py::test_between_hash` (new) — equal queries hash equal and are `==`; different bounds or paths hash differently; a query using `.map(...)` before `.between(...)` has hash None (uncacheable).

## Risks
- Hash omissions: if `low` or `high` were missing from hashval, different ranges would share a query-cache entry (the #637 class of bug). Both bounds are included, and the hash test covers this.
- `freeze()` is applied to unhashable bounds (e.g. lists) so hashing does not raise; the comparison itself uses the original values.
- Swallowing `TypeError` differs from `<`/`>=`, which propagate it for incomparable types. This is intentional per AC-4. A `TypeError` raised inside a custom `__lt__` is also swallowed.
- `None` values give TypeError, so they do not match.
