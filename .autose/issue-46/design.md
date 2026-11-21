## Approach
Make the `cond` parameter of `Table.count` optional (default `None`). When `cond` is `None`, return `len(self)`, which uses `_read_table` (the read path required by the architecture) and does one storage read. Otherwise keep `len(self.search(cond))`, so the query cache and hashing behave as before. No storage, query, or cache code changes. The `TinyDB` default-table proxy forwards `count` to the table, so it needs no change.

## Files to change
- `tinydb/table.py` — make `count`'s `cond` optional, with a no-query branch.
- `tests/test_tinydb.py` — add tests for `count()` with no query (3 documents, empty table, equals `len(table)`, and the query case unchanged).

## Functions
- `tinydb/table.py::Table.count` — signature `count(self, cond: Optional[QueryLike] = None) -> int`; if `cond is None`, return `len(self)`; else `len(self.search(cond))`. Update the docstring.

## Risks
- Explicit `count(None)` now also returns the total. The spec leaves this unspecified, so it is not tested.
- Query caching and hashing are untouched. The no-query path does not call `search`, so it neither reads nor fills the query cache.
- `Optional` is already imported in `table.py`, so no new import is needed.
