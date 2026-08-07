# secure-pipeline

Build → SAST → secrets scan → dependency scan → container scan → sign →
gate → deploy.

Runnable workflow: [`.github/workflows/secure-pipeline.yml`](../../.github/workflows/secure-pipeline.yml)

## Status: skeleton (Phase 2, Day 7)

Right now this only has **build** and **deploy** — the image is built,
handed off via a build artifact (no registry needed yet), and deployed with
a smoke test proving it's serving traffic. No scanning exists yet.

## Roadmap

| Day | Adds |
|---|---|
| 8 | Semgrep (SAST) + secrets scan |
| 9 | Trivy (dependency + container scan) + CodeQL |
| 10 | Cosign (image signing) + policy gate — `deploy` starts depending on every scan job, so a high/critical finding blocks it |

## Why this exists

This is the "after" side of the contrast: the same
[`secure-app`](../../applications/secure-app) as `vulnerable-app`, minus the
planted flaws, run through a pipeline that would have caught them had they
been there. Once the gate lands (Day 10), this repo's own PRs into `main`
are required to pass it too — the same rule the project demonstrates,
applied to itself.

Compare against [`insecure-pipeline`](../insecure-pipeline).
