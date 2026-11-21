# Test report — issue #2

Written by the pipeline script from pytest output (ADR-007), not by the agent.

- Acceptance criteria: AC-1, AC-2, AC-3, AC-4
- Missing per-criterion tests: none
- `python -m pytest` exit code: 0
- Result: **PASS**

```
============================= test session starts ==============================
platform linux -- Python 3.12.16, pytest-9.2.0, pluggy-1.7.0
rootdir: /home/runner/work/tinydb/tinydb/work
configfile: pytest.ini
plugins: cov-7.1.0
collected 232 items

tests/test_autose_issue.py ....                                          [  1%]
tests/test_middlewares.py .........                                      [  5%]
tests/test_operations.py ..............                                  [ 11%]
tests/test_queries.py ..................................                 [ 26%]
tests/test_storages.py ...........s..                                    [ 32%]
tests/test_tables.py ...............................                     [ 45%]
tests/test_tinydb.py ................................................... [ 67%]
...............................................................          [ 94%]
tests/test_utils.py ............                                         [100%]

======================== 231 passed, 1 skipped in 1.16s ========================

```
