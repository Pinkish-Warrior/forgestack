# Lessons learned

Real gotchas hit while building this, not staged for the writeup. Each one
cost real debugging time and changed something in the repo — that's the
bar for inclusion here, not "things that could theoretically go wrong."

## Security tooling gaps

**A required scan can pass clean and still be wrong.** [PR #5](https://github.com/Pinkish-Warrior/forgestack/pull/5)
reintroduced `vulnerable-app`'s exact SQL injection into `secure-app` to
prove the gate blocks something real. It did block — but the specific
job named `SAST (Semgrep)` passed: "Ran 82 rules on 6 files: 0 findings"
against an unambiguous injection. Root cause: the rule matched an exact
AST shape (`$SQL = f"..." ... $DB.execute($SQL)`) that only recognizes a
single f-string literal. Both apps build their query from two *adjacent*
f-string literals (`f"SELECT ... " f"WHERE ..."`) — Python merges these
at parse time, but the rule's shape-match didn't. The rule had likely
never actually fired against real code since it was written; nobody
noticed because no PR had touched that code path. Fixed by rewriting it
in taint mode (tracks the tainted value through concatenation instead of
requiring an exact shape), then verified against the real files in both
apps, not synthetic snippets — the distinction that would have caught
this the first time.

**A job showing green isn't the same as the job being the gate.**
Same PR #5 test: the check that actually blocked the merge was `CodeQL`
— GitHub's native code-scanning status check, a side effect of the
`codeql-action/analyze` step's SARIF upload. The pipeline's own job,
named `SAST (CodeQL)`, always shows green regardless of findings, by
design — `codeql-action/analyze` uploads results, it doesn't fail the
job. First read of this looked like a second, independent GHAS scan was
silently covering for a broken gate; `gh api repos/.../code-scanning/default-setup`
showed `state: not-configured`, ruling that out — there's no second scan,
just one feature (GitHub code scanning) posting a status check under a
different name than the job that triggers it. The gate was never broken,
just confusingly split across two similarly-named checks. Worth knowing
before assuming a green job means "no alerts."

## CI/CD & GitHub mechanics

**Required checks only count from the PR's own `pull_request` event —
not a `workflow_dispatch` run on the identical commit SHA.** PR #4
(docs-only) touched nothing in `secure-pipeline.yml`'s `paths:` filter,
so no `pull_request` event ever fired for it. A manual `workflow_dispatch`
run on the same SHA passed all 10 jobs, but GitHub didn't credit any of
them to the PR — confirmed via GraphQL `statusCheckRollup`, which showed
only an unrelated default `CodeQL` check attached. The PR was permanently
`BLOCKED`, not just slow. Fixed short-term with a one-line comment to
trigger a real event; fixed for good in PR #8 by widening the path filter
to include `docs/**`, `README.md`, and `pipelines/**`. PR #9 (a genuine
docs-only README pass) later confirmed the fix holds on a second real
case, not just the one it was written for.

**Squash-merge breaks git ancestry on the next PR.** GitHub's squash
merge creates a new commit on `main` with no history link back to `dev`'s
original commits. Any file touched by that squash shows an "add/add"
conflict on the next diff — even a trivial one-line change — because git
has no shared blob for a 3-way merge. Standing fix: merge `main` back
into `dev` immediately after every PR lands, before starting new work.

**Local `main` doesn't move on its own.** It only updates on explicit
`fetch`/`pull`, so it silently drifts behind `origin/main` while all real
work happens on `dev`. Caught it 3 commits stale once, then again 1
commit stale in a later session — the second catch is exactly why the
standing habit (sync local `main` from `origin/main` at the *start* of
every session, not just after a PR) exists: it's not a one-time fix, it's
a check that has to run every time.

**Semgrep's `# nosemgrep: <rule-id>` only suppresses a finding on the
same line or the line immediately above** — an explanatory comment
sitting between the suppression and the flagged code breaks it silently,
with no error to flag the miss.

**`aquasecurity/trivy-action` tags are `v`-prefixed** (`v0.24.0`, not
`0.24.0`) — the bare version fails the job at "Set up job," before any
scanning even starts.

## Environment quirks

**macOS's AirPlay Receiver squats on port 5000.** Both apps default to
it; any local run needs a different host port (5100/5101 here) or
AirPlay Receiver disabled in System Settings. Affects both the
containerized and un-containerized run paths — see
[`WALKTHROUGH.md`](../WALKTHROUGH.md).

**Neither app resets its database between runs.** Re-running the exploit
or the manual `curl` walkthrough against the same long-lived containers
hits `409 username already exists` on the second pass, and leaked-row
counts grow on repeat runs against `vulnerable-app`. Not a changing
vulnerability — cumulative test data. `make demo` avoids this by tearing
containers down after every run, so each invocation starts from an empty
database.

**GHCR image names must be lowercase, but Cosign's
`certificate-identity-regexp` must keep the repo's real case**
(`Pinkish-Warrior/forgestack`) — that's what's embedded in the GitHub
OIDC token's certificate. Lowercasing both by reflex breaks verification
silently (the regexp just never matches).
