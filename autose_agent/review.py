"""Independent reviewer (stage 6, ADR-008).

Runs in its own job with a read-only checkout token. Sees only the issue, the diff
and the repository at the PR head with .autose/ (implementer artifacts) removed.
"""
import argparse
import os
import pathlib
import re
import shutil

from common import (REPO, REVIEWER_ALLOWED, REVIEWER_TOOLS, RUN_URL, fetch_issue, gh,
                    gh_output, load_prompt, log, run_agent, sh, untrusted_issue,
                    usage_summary)

MAX_TURNS = int(os.environ.get("AUTOSE_REVIEWER_MAX_TURNS") or "25")
VERDICT = re.compile(r"^\s*\**VERDICT:\s*(approve|changes-code|changes-approach)\**\s*$", re.M | re.I)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--issue", type=int, required=True)
    ap.add_argument("--round", type=int, required=True)
    ap.add_argument("--final", action="store_true")
    ap.add_argument("--work", default="work")
    ap.add_argument("--out", required=True)
    ap.add_argument("--pr", help="PR number (default: open PR from autose/issue-N)")
    ap.add_argument("--variant", choices=("default", "with-claims", "plain", "adversarial"), default="default",
                    help="Decision-experiment variants (experiment/variants.md)")
    a = ap.parse_args()

    work = pathlib.Path(a.work).resolve()
    out = pathlib.Path(a.out).resolve()
    out.mkdir(parents=True, exist_ok=True)
    usage = out / f"usage-review-{a.round}.jsonl"

    branch = f"autose/issue-{a.issue}"
    pr = a.pr or gh("pr", "list", "--repo", REPO, "--head", branch, "--state", "open",
                    "--json", "number", "--jq", ".[0].number")

    # Variant with-claims: reviewer ALSO sees what the implementer said (PR body + artifacts).
    claims = ""
    if a.variant == "with-claims":
        claims = gh("pr", "view", str(pr), "--repo", REPO, "--json", "body", "--jq", ".body") if pr else ""
        for f in sorted((work / ".autose").rglob("*.md")):
            claims += f"\n\n--- {f.relative_to(work)} ---\n{f.read_text()[:8000]}"

    # Withhold implementer artifacts (ADR-003/004/008).
    shutil.rmtree(work / ".autose", ignore_errors=True)
    sh(["git", "fetch", "-q", "origin", "master"], cwd=work)
    diff = sh(["git", "diff", "origin/master...HEAD", "--", ".", ":(exclude).autose"], cwd=work).stdout
    head = sh(["git", "rev-parse", "--short", "HEAD"], cwd=work).stdout.strip()
    title, body = fetch_issue(a.issue)

    # ADR-012: default = neutral prompt + checklist; "adversarial" = the ADR-008 prompt.
    prompt = load_prompt({"plain": "review_plain", "adversarial": "review_adversarial"}.get(a.variant, "review"),
                         issue=untrusted_issue(a.issue, title, body),
                         diff=diff[:60000] or "(empty diff)")
    if claims:
        prompt += ("\n\nThe implementer's own description of the change and its working notes:\n"
                   f"<implementer_notes>\n{claims[:30000]}\n</implementer_notes>\n")
    text = run_agent(f"6-review-{a.round}-{a.variant}", prompt,
                     work, REVIEWER_TOOLS, REVIEWER_ALLOWED, MAX_TURNS, usage)

    matches = VERDICT.findall(text)
    verdict = matches[-1].lower() if matches else "malformed"
    if (verdict == "approve" and a.variant != "plain"
            and not re.search(r"^##\s*Checklist", text, re.M | re.I)):
        verdict = "malformed"  # approval without evidence checklist (ADR-008)

    note = ""
    if verdict == "malformed":
        note = "\n\n> Verdict missing or approval without checklist: treated as a stop (ADR-007)."
    elif a.final and verdict != "approve":
        note = "\n\n> Two review rounds used. Leaving the decision to a human maintainer."
    review_md = (f"# Independent review — round {a.round} (variant: {a.variant})\n\n"
                 f"Reviewed commit `{head}` for #{a.issue}. Run: {RUN_URL}\n"
                 f"Reviewer inputs: issue text, diff, repository at PR head (implementer artifacts removed).\n\n"
                 f"{text.strip() or '(reviewer produced no output)'}{note}\n\n"
                 f"---\nParsed verdict: `{verdict}` · Usage: {usage_summary(usage)}\n")
    (out / f"review-{a.round}.md").write_text(review_md)
    if pr:
        gh("pr", "comment", str(pr), "--repo", REPO, "--body-file", "-", input=review_md[:60000])
    else:
        log("no open PR found to comment on")
    gh_output("verdict", verdict)


if __name__ == "__main__":
    main()
