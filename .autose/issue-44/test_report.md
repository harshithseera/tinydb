# Test report — issue #44

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
collected 235 items

tests/test_autose_issue.py .......                                       [  2%]
tests/test_middlewares.py .........                                      [  6%]
tests/test_operations.py ..............                                  [ 12%]
tests/test_queries.py ..................................                 [ 27%]
tests/test_storages.py ...........s..                                    [ 33%]
tests/test_tables.py ...............................                     [ 46%]
tests/test_tinydb.py ................................................... [ 68%]
...............................................................          [ 94%]
tests/test_utils.py ............                                         [100%]

======================== 234 passed, 1 skipped in 0.42s ========================

```
