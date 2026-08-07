# secure-pipeline

Build → SAST → secrets scan → dependency scan → container scan → sign →
gate → deploy.

Runnable workflow: [`.github/workflows/secure-pipeline.yml`](../../.github/workflows/secure-pipeline.yml)

## Status: build + SAST + secrets scan + deploy (Phase 2, Day 8)

`build` produces the image and hands it to `deploy` via a build artifact
(no registry needed yet). `sast` and `secrets-scan` run against source in
parallel with `build`. `deploy` now depends on all three — a finding in
either scan job fails that job, which blocks `deploy` through the job's
normal `needs` failure propagation.

- **SAST** — [Semgrep](https://semgrep.dev), rules in
  [`security/semgrep/semgrep-rules.yaml`](../../security/semgrep/semgrep-rules.yaml):
  two custom rules that target `vulnerable-app`'s exact planted flaws
  (SQL built via f-string, hardcoded Flask `SECRET_KEY`), plus the
  `p/security-audit` registry ruleset for broader coverage.
- **Secrets scan** — [Gitleaks](https://github.com/gitleaks/gitleaks),
  default ruleset, via `gitleaks/gitleaks-action`.

## Roadmap

| Day | Adds |
|---|---|
| 9 | Trivy (dependency + container scan) + CodeQL |
| 10 | Cosign (image signing) + a formal policy gate — same `needs`-based blocking as today, made explicit and extended to cover severity thresholds |

## Why this exists

This is the "after" side of the contrast: the same
[`secure-app`](../../applications/secure-app) as `vulnerable-app`, minus the
planted flaws, run through a pipeline that would have caught them had they
been there. Once the gate lands (Day 10), this repo's own PRs into `main`
are required to pass it too — the same rule the project demonstrates,
applied to itself.

Compare against [`insecure-pipeline`](../insecure-pipeline).
