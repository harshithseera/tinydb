Fixes #1

Automated change produced by the AutoSE workflow (round 1). A human must review and merge; the workflow never merges.

- Run: https://github.com/harshithseera/tinydb/actions/runs/44856860179
- Artifacts: `.autose/issue-1/` on this branch (spec.md, design.md, diff.patch, test_report.md, usage.jsonl)
- Usage: 4 agent calls, input 30 + cache-write 38919 + cache-read 189772 tokens, output 6120 tokens

### Test report

# Test report — issue #1

Written by the pipeline script from pytest output (ADR-007), not by the agent.

- Acceptance criteria: AC-1, AC-2, AC-3, AC-4
- Missing per-criterion tests: none
- `python -m pytest` exit code: 0
- Result: **PASS**

PR: https://github.com/harshithseera/tinydb/pull/15
