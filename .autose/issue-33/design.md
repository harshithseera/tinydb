## Approach
Reading `Table` shows the code already meets every acceptance criterion. `update`/`insert_multiple` each call `_update_table` once, which does one `read()` and one `write()`. `search` serves repeated cacheable queries from the per-table `LRUCache` without touching storage (ADR-1, ADR-2). The issue gives no figures or reproducer, so no safe algorithmic change is justified, and changing the whole-database storage model would break ADR-1. The change is therefore a set of regression tests that use a counting in-memory `Storage` to pin the I/O counts (AC-1..AC-3) and cache invalidation on writes (AC-4). No production code changes. Users who need more speed on large databases should use `CachingMiddleware`, which ADR-1 names as the place for performance work. The tests are the deliverable, and the docs can mention this.

## Files to change
- `tests/test_tables.py` — add counting-storage tests for AC-1 to AC-4.
- `docs/usage.rst` — optionally add a short note recommending `CachingMiddleware` for large databases.

## Functions
- `tests/test_tables.py::CountingStorage` (new) — `Storage` subclass wrapping an in-memory dict that counts `read()` and `write()` calls.
- `tests/test_tables.py::test_update_single_write` (new) — AC-1: 1000 docs, `update({'x': 1}, where('n') > 10)` does exactly one write, and all matching docs have `x == 1`.
- `tests/test_tables.py::test_repeated_search_no_reads` (new) — AC-2: the second identical `search` does zero reads and returns equal results.
- `tests/test_tables.py::test_insert_multiple_single_write` (new) — AC-3: 500 docs are inserted with one write, and `len` grows by 500.
- `tests/test_tables.py::test_search_cache_invalidated_on_write` (new) — AC-4: after `update` and after `remove`, the same query returns fresh results.

## Risks
- The tests pin exact read/write counts, so they can become brittle if internals such as `_get_next_id` read the storage. Count only the call under test, and reset the counters before it.
- The `len` check in AC-3 itself calls `read()`, so make that assertion after the counts are captured.
- No change to query hashing or the cache, so the stale-cache and #637-style risks are unchanged. The AC-4 test guards them.
- The tests do not prove a speedup. Wall-clock performance is out of scope and untested.
