"""Builder pipeline: stages 1-5 as a fixed, code-driven sequence (ADR-002).

Every pass/fail decision is made here, deterministically (ADR-007). The agent only
writes files in the working copy; this script commits, pushes and opens the PR.
"""
import argparse
import os
import pathlib
import re
import shutil
import sys

from common import (BUILDER_ALLOWED, BUILDER_TOOLS, REPO, RUN_URL, fetch_issue, gh,
                    gh_output, load_prompt, log, run_agent, sh, untrusted_issue,
                    usage_summary)

MAX_TURNS = int(os.environ.get("AUTOSE_BUILDER_MAX_TURNS", "30"))
IMPL_ATTEMPTS = int(os.environ.get("AUTOSE_IMPL_ATTEMPTS", "3"))
ALLOWED_PREFIXES = ("tinydb/", "tests/", "docs/")
BOT = ["-c", "user.name=github-actions[bot]",
       "-c", "user.email=41898282+github-actions[bot]@users.noreply.github.com"]


class StageFailed(Exception):
    def __init__(self, stage, artifact, reason):
        super().__init__(reason)
        self.stage, self.artifact, self.reason = stage, artifact, reason


class Run:
    def __init__(self, issue, work):
        self.issue = issue
        self.work = work
        self.branch = f"autose/issue-{issue}"
        self.art = work / ".autose" / f"issue-{issue}"
        self.usage = self.art / "usage.jsonl"
        self.title, self.body = fetch_issue(issue)
        self.issue_block = untrusted_issue(issue, self.title, self.body)

    # ---------- git / GitHub (script only) ----------
    def git(self, *args, check=True):
        return sh(["git", *args], cwd=self.work, check=check)

    def commit(self, message):
        self.git("add", "-A")
        if self.git("diff", "--cached", "--quiet", check=False).returncode != 0:
            self.git(*BOT, "commit", "-q", "-m", message)

    def push(self):
        token = os.environ["GH_TOKEN"]
        url = f"https://x-access-token:{token}@github.com/{REPO}.git"
        sh(["git", "push", "-q", "--force", url, f"HEAD:refs/heads/{self.branch}"], cwd=self.work)

    def comment(self, text):
        gh("issue", "comment", str(self.issue), "--repo", REPO, "--body-file", "-", input=text)

    def read(self, name):
        p = self.art / name
        return p.read_text() if p.exists() else f"({name} not present)"

    def agent(self, label, prompt):
        return run_agent(label, prompt, self.work, BUILDER_TOOLS, BUILDER_ALLOWED,
                         MAX_TURNS, self.usage)

    def code_diff(self, name_only=False):
        self.git("add", "-A")
        # Diff against the merge-base so later commits on master are not counted as ours.
        base = self.git("merge-base", "origin/master", "HEAD").stdout.strip()
        args = ["diff", "--cached", base]
        if name_only:
            args.append("--name-only")
        args += ["--", ".", ":(exclude).autose"]
        return self.git(*args).stdout

    def append_failure(self, artifact, stage, reason):
        p = self.art / artifact
        with open(p, "a") as f:
            f.write(f"\n\n---\n## Stage {stage} check: FAILED\n\n{reason}\n\nRun stopped. {RUN_URL}\n")

    # ---------- stages ----------
    def stage1_requirements(self):
        skill = (pathlib.Path(__file__).parent / "skill/requirements-spec-builder/SKILL.md").read_text()
        self.agent("1-requirements", load_prompt(
            "requirements", skill=skill, issue=self.issue_block, art=self.rel("spec.md")))
        ok, reason = check_spec(self.art / "spec.md")
        self.commit(f"autose #{self.issue}: stage 1 requirements ({'pass' if ok else 'fail'})")
        if not ok:
            raise StageFailed(1, "spec.md", reason)

    def stage2_design(self, extra=""):
        arch = (pathlib.Path(__file__).parent / "context/ARCHITECTURE.md").read_text()
        self.agent("2-design", load_prompt(
            "design", architecture=arch, issue=self.issue_block, spec=self.read("spec.md"),
            extra=extra or "None.", art=self.rel("design.md")))
        ok, reason = check_design(self.art / "design.md", self.work)
        self.commit(f"autose #{self.issue}: stage 2 design ({'pass' if ok else 'fail'})")
        if not ok:
            raise StageFailed(2, "design.md", reason)

    def stage3_implement(self, feedback):
        self.agent("3-implement", load_prompt(
            "implement", issue=self.issue_block, spec=self.read("spec.md"),
            design=self.read("design.md"), feedback=feedback or "None (first attempt)."))
        names = [n for n in self.code_diff(name_only=True).splitlines() if n]
        diff = self.code_diff()
        (self.art / "diff.patch").write_text(diff)
        if not names:
            return False, "The implementation produced no code changes."
        bad = [n for n in names if not n.startswith(ALLOWED_PREFIXES)]
        if bad:
            return False, f"Changed files outside {ALLOWED_PREFIXES}: {bad}"
        for cmd in (["python", "-m", "compileall", "-q", "tinydb"], ["python", "-c", "import tinydb"]):
            r = sh(cmd, cwd=self.work, check=False)
            if r.returncode != 0:
                return False, f"Build check `{' '.join(cmd)}` failed:\n```\n{(r.stdout + r.stderr)[-3000:]}\n```"
        return True, ""

    def stage4_test(self):
        ac_ids = acceptance_ids(self.art / "spec.md")
        self.agent("4-test", load_prompt(
            "tests", issue=self.issue_block, spec=self.read("spec.md"),
            diff=self.read("diff.patch"),
            names=", ".join(f"test_ac{n}_<what>" for n in ac_ids)))
        tests_text = "\n".join(p.read_text(errors="ignore") for p in (self.work / "tests").rglob("*.py"))
        missing = [n for n in ac_ids if not re.search(rf"def test_ac{n}(_|\()", tests_text)]
        r = sh(["python", "-m", "pytest", "-p", "no:cacheprovider", "-q", "--no-cov", "-rf"],
               cwd=self.work, check=False, timeout=600)
        out = (r.stdout + r.stderr)[-6000:]
        passed = r.returncode == 0 and not missing
        report = [f"# Test report — issue #{self.issue}", "",
                  "Written by the pipeline script from pytest output (ADR-007), not by the agent.", "",
                  f"- Acceptance criteria: {', '.join(f'AC-{n}' for n in ac_ids)}",
                  f"- Missing per-criterion tests: {', '.join(f'AC-{n}' for n in missing) or 'none'}",
                  f"- `python -m pytest` exit code: {r.returncode}",
                  f"- Result: **{'PASS' if passed else 'FAIL'}**", "", "```", out, "```"]
        (self.art / "test_report.md").write_text("\n".join(report) + "\n")
        self.code_diff()
        (self.art / "diff.patch").write_text(self.code_diff())
        reason = ""
        if missing:
            reason += f"No test named test_ac<n>_* for: {missing}. "
        if r.returncode != 0:
            reason += f"pytest failed (exit {r.returncode}):\n```\n{out[-3000:]}\n```"
        return passed, reason

    def build_loop(self, review_feedback=""):
        """Stage 3 <-> 4 retry loop, then one return to design (ADR-002)."""
        feedback = review_feedback
        for design_round in (1, 2):
            for attempt in range(1, IMPL_ATTEMPTS + 1):
                ok, reason = self.stage3_implement(feedback)
                if ok:
                    ok, reason = self.stage4_test()
                    self.commit(f"autose #{self.issue}: stages 3-4 attempt {attempt} "
                                f"({'pass' if ok else 'fail'})")
                    if ok:
                        return
                    feedback = f"Attempt {attempt} failed the testing check:\n{reason}"
                else:
                    self.commit(f"autose #{self.issue}: stage 3 attempt {attempt} (fail)")
                    feedback = f"Attempt {attempt} failed the build check:\n{reason}"
                log(f"attempt {attempt} failed: {reason[:300]}")
            if design_round == 1:
                log("implementation budget used; returning to design once")
                self.stage2_design(extra="The previous design could not be implemented so "
                                         f"that all tests pass. Last failure:\n{feedback}")
                feedback = "Design was revised after repeated failures; implement the new design."
        artifact = "test_report.md" if (self.art / "test_report.md").exists() else "diff.patch"
        raise StageFailed(4, artifact, f"Budget used up ({IMPL_ATTEMPTS} attempts x 2 designs). "
                                       f"Last failure:\n{feedback}")

    def stage5_release(self, round_no):
        pr_md = "\n".join([
            f"Fixes #{self.issue}", "",
            f"Automated change produced by the AutoSE workflow (round {round_no}). "
            "A human must review and merge; the workflow never merges.", "",
            f"- Run: {RUN_URL}",
            f"- Artifacts: `.autose/issue-{self.issue}/` on this branch "
            "(spec.md, design.md, diff.patch, test_report.md, usage.jsonl)",
            f"- Usage: {usage_summary(self.usage)}", "",
            "### Test report", "", self.read("test_report.md").split("```")[0].strip(),
        ])
        (self.art / "pr.md").write_text(pr_md + "\n")
        self.commit(f"autose #{self.issue}: stage 5 release")
        self.push()
        existing = gh("pr", "list", "--repo", REPO, "--head", self.branch, "--state", "open",
                      "--json", "url", "--jq", ".[0].url")
        if existing:
            gh("pr", "edit", existing, "--repo", REPO, "--body-file", str(self.art / "pr.md"))
            url = existing
        else:
            url = gh("pr", "create", "--repo", REPO, "--base", "master", "--head", self.branch,
                     "--title", f"[autose] {self.title[:80]} (#{self.issue})",
                     "--body-file", str(self.art / "pr.md"))
        state = gh("pr", "view", url, "--repo", REPO, "--json", "state", "--jq", ".state")
        if state != "OPEN":
            raise StageFailed(5, "pr.md", f"PR {url} is {state}, expected OPEN")
        with open(self.art / "pr.md", "a") as f:
            f.write(f"\nPR: {url}\n")
        self.commit(f"autose #{self.issue}: record PR link")
        self.push()
        return url

    def rel(self, name):
        return str((self.art / name).relative_to(self.work))


# ---------- deterministic checks (ADR-007) ----------
AC_LINE = re.compile(r"^\s*[-*]?\s*\**AC-(\d+)\**\s*:\s*Given\b.+\bWhen\b.+\bThen\b.+", re.I | re.M)


def section(text, heading):
    m = re.search(rf"^##\s+{re.escape(heading)}\s*$(.*?)(?=^##\s|\Z)", text, re.M | re.S | re.I)
    return m.group(1) if m else None


def acceptance_ids(spec_path):
    text = spec_path.read_text() if spec_path.exists() else ""
    sec = section(text, "Acceptance criteria") or ""
    return [int(n) for n in dict.fromkeys(AC_LINE.findall(sec))]


def check_spec(path):
    if not path.exists():
        return False, "spec.md was not written."
    text = path.read_text()
    if section(text, "Acceptance criteria") is None:
        return False, "spec.md has no `## Acceptance criteria` section."
    if not acceptance_ids(path):
        return False, "No acceptance criterion matches `AC-<n>: Given … When … Then …`."
    blocking = section(text, "Blocking open questions")
    if blocking is None:
        return False, "spec.md has no `## Blocking open questions` section."
    lines = [l.strip(" -*\t") for l in blocking.strip().splitlines() if l.strip(" -*\t")]
    if lines and not (len(lines) == 1 and lines[0].rstrip(".").lower() == "none"):
        return False, "Blocking open questions remain, so the criteria cannot be made testable:\n" + blocking.strip()
    return True, ""


def check_design(path, work):
    if not path.exists():
        return False, "design.md was not written."
    text = path.read_text()
    files_sec = section(text, "Files to change")
    funcs_sec = section(text, "Functions")
    if files_sec is None or funcs_sec is None:
        return False, "design.md needs `## Files to change` and `## Functions` sections."
    files = re.findall(r"`([\w./-]+\.py)`", files_sec)
    if not any((work / f).exists() for f in files):
        return False, f"`## Files to change` names no existing file (found {files})."
    for f in files:
        if not (work / f).exists() and not f.startswith("tests/"):
            return False, f"Design names new file `{f}` outside tests/."
    entries = re.findall(r"`([\w./-]+\.py)::([\w.]+)`(.*)", funcs_sec)
    if not entries:
        return False, "`## Functions` lists no `path.py::name` entries."
    for f, name, rest in entries:
        p = work / f
        if not p.exists():
            if f.startswith("tests/"):
                continue
            return False, f"`{f}` (in `## Functions`) does not exist."
        if "(new)" in rest:
            continue
        leaf = name.split(".")[-1]
        if not re.search(rf"\b(def|class)\s+{re.escape(leaf)}\b", p.read_text()):
            return False, f"`{f}::{name}` not found in {f} and not marked (new)."
    return True, ""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--issue", type=int, required=True)
    ap.add_argument("--from-stage", type=int, choices=(1, 2, 3), default=1)
    ap.add_argument("--round", type=int, default=1)
    ap.add_argument("--review-file")
    ap.add_argument("--work", default="work")
    a = ap.parse_args()

    run = Run(a.issue, pathlib.Path(a.work).resolve())
    run.git("fetch", "-q", "origin", "master")
    if a.from_stage == 1:
        run.git("checkout", "-q", "-B", run.branch, "origin/master")
        shutil.rmtree(run.art, ignore_errors=True)
        run.comment(f"AutoSE run started for #{a.issue}: {RUN_URL}")
    else:
        run.git("checkout", "-q", "-B", run.branch, "HEAD")
    run.art.mkdir(parents=True, exist_ok=True)

    review_text = ""
    if a.review_file:
        review_text = pathlib.Path(a.review_file).read_text()
        shutil.copy(a.review_file, run.art / f"review-{a.round - 1}.md")
        shutil.copy(a.review_file, run.art / "review.md")
        run.commit(f"autose #{a.issue}: record review round {a.round - 1}")

    try:
        if a.from_stage == 1:
            run.stage1_requirements()
        if a.from_stage <= 2:
            run.stage2_design(extra=f"Reviewer feedback to address:\n{review_text}" if review_text else "")
        run.build_loop(review_feedback=(f"Reviewer feedback to address:\n{review_text}"
                                        if review_text and a.from_stage == 3 else ""))
        url = run.stage5_release(a.round)
    except StageFailed as e:
        run.append_failure(e.artifact, e.stage, e.reason)
        run.commit(f"autose #{a.issue}: stopped at stage {e.stage}")
        run.push()
        tree = f"https://github.com/{REPO}/tree/{run.branch}/.autose/issue-{a.issue}"
        run.comment(f"AutoSE stopped at **stage {e.stage}**: see `{e.artifact}` ({tree}).\n\n"
                    f"{e.reason[:3000]}\n\nRun: {RUN_URL}")
        gh_output("status", f"stopped-stage-{e.stage}")
        sys.exit(1)
    gh_output("status", "pr-open")
    gh_output("pr", url)
    run.comment(f"AutoSE opened {url} (round {a.round}). CI and independent review follow. "
                f"Usage so far: {usage_summary(run.usage)}")


if __name__ == "__main__":
    main()
