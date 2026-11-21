# Test report — issue #35

Written by the pipeline script from pytest output (ADR-007), not by the agent.

- Acceptance criteria: AC-1, AC-2, AC-3, AC-4, AC-5
- Missing per-criterion tests: none
- `python -m pytest` exit code: 0
- Result: **PASS**

```
============================= test session starts ==============================
platform linux -- Python 3.12.16, pytest-9.2.0, pluggy-1.7.0
rootdir: /home/runner/work/tinydb/tinydb/work
configfile: pytest.ini
plugins: cov-7.1.0
collected 233 items

tests/test_autose_issue.py .....                                         [  2%]
tests/test_middlewares.py .........                                      [  6%]
tests/test_operations.py ..............                                  [ 12%]
tests/test_queries.py ..................................                 [ 26%]
tests/test_storages.py ...........s..                                    [ 32%]
tests/test_tables.py ...............................                     [ 45%]
tests/test_tinydb.py ................................................... [ 67%]
...............................................................          [ 94%]
tests/test_utils.py ............                                         [100%]

======================== 232 passed, 1 skipped in 0.44s ========================

```
