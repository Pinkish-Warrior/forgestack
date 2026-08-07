# secure-pipeline

Build → SAST → secrets scan → dependency scan → container scan → sign →
gate → deploy.

Runnable workflow: [`.github/workflows/secure-pipeline.yml`](../../.github/workflows/secure-pipeline.yml)

## Status: build + 5 scan jobs + deploy (Phase 2, Day 9)

`build` produces the image and hands it to `deploy` (and `container-scan`)
via a build artifact (no registry needed yet). `sast`, `secrets-scan`,
`dependency-scan`, and `codeql` run against source in parallel with
`build`; `container-scan` needs the built image, so it runs after `build`.
`deploy` now depends on all five scan jobs — a finding in any of them
fails that job, which blocks `deploy` through the job's normal `needs`
failure propagation.

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

## Roadmap

| Day | Adds |
|---|---|
| 10 | Cosign (image signing) + a formal policy gate — same `needs`-based blocking as today, made explicit and extended to cover severity thresholds |

## Why this exists

This is the "after" side of the contrast: the same
[`secure-app`](../../applications/secure-app) as `vulnerable-app`, minus the
planted flaws, run through a pipeline that would have caught them had they
been there. Once the gate lands (Day 10), this repo's own PRs into `main`
are required to pass it too — the same rule the project demonstrates,
applied to itself.

Compare against [`insecure-pipeline`](../insecure-pipeline).
