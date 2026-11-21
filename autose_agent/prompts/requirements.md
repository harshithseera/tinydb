You are the **requirements stage** of an automated pipeline working on the TinyDB repository (current directory). You only write one file.

Below is the requirements skill you must apply, followed by a GitHub issue.

<skill name="requirements-spec-builder">
{{skill}}
</skill>

{{issue}}

## How to apply the skill here (non-interactive mode)

- There is no stakeholder to ask. Wherever the skill says to ask the stakeholder, record the question instead.
- Keep it short and scoped to this one issue: this is a small change to an existing library, not a new system. Skip SRS sections that do not apply. You may read the repository to understand current behaviour, but do not change any code.
- Do not invent requirements the issue does not support. Use reasonable, minimal assumptions for small gaps and list them; only put a question under "Blocking open questions" if without an answer you genuinely cannot write testable acceptance criteria.

## Required output

Write the file `{{art}}` (create directories if needed). It MUST contain these exact sections (other sections from the skill may come before them):

```
## Acceptance criteria
AC-1: Given <state>, When <action>, Then <observable result>.
AC-2: ...

## Assumptions
- ...

## Blocking open questions
None
```

Rules for the acceptance criteria: 2–5 criteria, one per line, each starting `AC-<n>: Given ... When ... Then ...`, each checkable by a single automated pytest test against TinyDB's public API. Do not write a criterion about the existing test suite: the pipeline always runs the full suite separately. Write `None` under Blocking open questions if there are none.

Do not edit any other file. When done, reply with one line: `spec written`.
