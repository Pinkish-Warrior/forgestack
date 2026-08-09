# secure-pipeline

Build → SAST → secrets scan → dependency scan → container scan → sign →
gate → deploy.

Runnable workflow: [`.github/workflows/secure-pipeline.yml`](../../.github/workflows/secure-pipeline.yml)

## Status: complete (Phase 2, Day 10)

`build` produces the image, tags it for GHCR, and pushes it —
`container-scan` and `deploy` each get the exact bits they need (a saved
artifact for the former, a pull-by-digest for the latter). `sast`,
`secrets-scan`, `dependency-scan`, and `codeql` run against source in
parallel with `build`; `container-scan` needs the built image, so it runs
after `build`.

- **SAST** — [Semgrep](https://semgrep.dev), rules in
  [`security/semgrep/semgrep-rules.yaml`](../../security/semgrep/semgrep-rules.yaml):
  two custom rules that target `vulnerable-app`'s exact planted flaws
  (SQL built via f-string, hardcoded Flask `SECRET_KEY`), plus the
  `p/security-audit` registry ruleset for broader coverage.
- **SAST** — [CodeQL](https://codeql.github.com), GitHub-native, config in
  [`security/codeql/codeql-config.yml`](../../security/codeql/codeql-config.yml).
  Deeper dataflow analysis than Semgrep, at the cost of a slower job.
- **Secrets scan** — [Gitleaks](https://github.com/gitleaks/gitleaks),
  default ruleset, via `gitleaks/gitleaks-action`.
- **Dependency scan** — [Trivy](https://trivy.dev) filesystem scan against
  `applications/secure-app` (mainly `requirements.txt`), config in
  [`security/trivy/trivy-config.yaml`](../../security/trivy/trivy-config.yaml).
- **Container scan** — Trivy image scan against the built `secure-app`
  image, same config file, CRITICAL/HIGH only, fails closed
  (`exit-code: 1`) on an unfixed match.
- **Sign** — [Cosign](https://github.com/sigstore/cosign), keyless
  (Sigstore/Fulcio/Rekor — no private key managed anywhere). `sign` only
  runs once every scan job above has passed.
- **Gate** — `cosign verify` against the identity/issuer policy in
  [`security/cosign/cosign-policy.yaml`](../../security/cosign/cosign-policy.yaml).
  This is the formal policy gate: `deploy` needs `gate`, and `gate` needs a
  cryptographically valid signature, so passing is proof the image cleared
  every scan — not just evidence the jobs were wired up to run.

`main` also has branch protection requiring all of these checks, so a
failing scan blocks the actual GitHub merge button on a PR, not just this
pipeline's own internal `deploy` step.

## Why this exists

This is the "after" side of the contrast: the same
[`secure-app`](../../applications/secure-app) as `vulnerable-app`, minus the
planted flaws, run through a pipeline that would have caught them had they
been there. This repo's own PRs into `main` are required to pass it too —
the same rule the project demonstrates, applied to itself.

### Where the gate lives

"The gate" is Semgrep, CodeQL, Gitleaks, Trivy, and Cosign's verify step —
and where it lives matters as much as what it checks. There are two places
a security check can sit:

- **After deploy** — code merges, ships, and *then* something scans it and
  reports "this shipped with a SQL injection." Useful for visibility, but
  the bug already reached users by the time anyone knows.
- **On the pull request, before merge** — opening a PR into `main` runs
  this pipeline as a required check. If any scan fails, the check fails,
  and branch protection means the Merge button isn't clickable. The bug
  never becomes part of `main` at all, let alone gets deployed.

`secure-pipeline.yml` is wired for the second one: it triggers on
`pull_request` (not just `push`), and every job in it — including `gate` —
is a required status check on `main`. That's what makes it a gate rather
than a report: prevention instead of detection, and it's structural, not a
policy someone could choose to ignore, since `enforce_admins` is on and
there's no bypass.

To be precise about what's actually been demonstrated versus what's
designed to happen: every real PR in this repo's history (#1-#4, #7) has
passed cleanly, since none of them introduced a genuine vulnerability. The
block was proven separately, on purpose:
[PR #5](https://github.com/Pinkish-Warrior/forgestack/pull/5) reintroduced
a real SQL injection into `secure-app` on a throwaway branch, came back
`BLOCKED` via the GitHub API, and was closed unmerged once confirmed. So
the mechanism isn't just live today — it's been tested against a real
failure and held.

Compare against [`insecure-pipeline`](../insecure-pipeline).
