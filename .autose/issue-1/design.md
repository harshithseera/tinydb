## Approach
`Table.search` currently hands the caller Document objects that are the same objects stored in `_query_cache` (the cache holds only a shallow list copy, `docs[:]`, and the first search returns the very `docs` whose elements were cached). We make the cache and the caller own separate documents: the cache keeps its own deep copies, and every return value (first search and cache hits) is built from deep copies as well. Copying happens only inside `Table.search`, so the storage contract, `_update_table` cache clearing and the query hashing/cacheability rules are untouched. A small private helper does the copy so both paths share it and preserve `doc_id` (and the document class). Nested values are covered by `copy.deepcopy`. The docstring note telling callers to treat results as read-only is updated.

## Files to change
- `tinydb/table.py` — import `deepcopy`; copy documents when storing into and when returning from the query cache in `search`; update docstring.
- `tests/test_tinydb.py` — add tests for the acceptance criteria.

## Functions
- `tinydb/table.py::Table.search` — store `[deepcopy(d) for d in docs]` in the cache; on a cache hit return deep copies of the cached documents; on a miss return `docs` (not shared with the cache); fix docstring.
- `tinydb/table.py::Table._copy_docs` (new) — returns a list of deep copies of the given documents, preserving `doc_id` and class.

## Risks
- Performance: extra deep copy per search (O(result size)), including on cache hits; acceptable for correctness.
- `deepcopy` of a custom `document_class` whose constructor needs `doc_id` relies on the default dict-subclass copy protocol (no `__init__` call); `Document` has `doc_id` as an instance attribute, which deepcopy preserves. Tests should assert `doc_id` is kept.
- Cache keys/hashing and `is_cacheable` logic are unchanged, so no change to #637-style hash behavior; `update`/`_update_table` still clears the cache (AC-4).
- Existing tests that assert identity of cached results, if any, may need adjusting.
- Other read methods (`get`, `all`, `__iter__`) already build fresh Documents from storage; not changed.
