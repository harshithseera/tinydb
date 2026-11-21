You are reviewing a pull request for the TinyDB repository (current directory, checked out at the pull request's latest commit). The change was written by a different agent; you do not have its reasoning.

{{issue}}

The pull request diff against master:

<diff>
{{diff}}
</diff>

Read the issue yourself and decide what a correct change must do. Read the changed code and the code around it, run the full test suite (`python -m pytest -p no:cacheprovider -q --no-cov`) and try the behaviour the issue asks for with `python -c "..."`. You cannot edit files, use git, or access the network.

## Output (your final message, exactly this structure)

```
## Findings
- [blocking|minor] `path:line` — problem
(or "- none")

## Checklist
- [x/ ] Every requirement in the issue is met
- [x/ ] Tests would fail without the change
- [x/ ] No unrelated or risky changes (CI, packaging, public API breaks)
- [x/ ] Full test suite passes

VERDICT: <approve|changes-code|changes-approach>
```

`changes-approach` = the overall design is wrong (wrong place, wrong API, misread issue); `changes-code` = fixable bugs or missing tests; `approve` = no blocking finding.

Run each shell command on its own: no `cd`, `&&`, `;` or pipes, because only plain `python -m pytest ...` and `python -c "..."` commands are permitted.
