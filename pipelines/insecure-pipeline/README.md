# insecure-pipeline

Build → deploy. No scanning, no gate.

Runnable workflow: [`.github/workflows/insecure-pipeline.yml`](../../.github/workflows/insecure-pipeline.yml)

## Stages

1. **Build** — `docker build` the [`vulnerable-app`](../../applications/vulnerable-app) image, no inspection of what went in.
2. **Deploy** — run the image and smoke-test that it's serving traffic. No SAST, no secrets scan, no dependency/container scan, no signing, no policy gate.

## Why this exists

It's the control, not the point. Without a "before," there's nothing to
measure the secure pipeline's "after" against — this is what lets the same
exploit get run against both apps and produce a different, provable outcome
(Phase 3, Days 11–12) instead of an asserted one.

It's also deliberately honest rather than artificially crippled: no
SAST/secrets/dependency/container scanning and no gate is the default state
of a lot of real production CI, not a strawman built to lose.

Every flaw documented in
[`vulnerable-app/README.md`](../../applications/vulnerable-app/README.md) —
the SQL injection, the hardcoded `SECRET_KEY`, the CVE-bearing Werkzeug pin,
the unpinned root-user Dockerfile — ships untouched here, because nothing in
this pipeline looks for them.

Compare against `secure-pipeline` (Phase 2, Days 7–10): the same build →
deploy shape, plus SAST, secrets scanning, dependency/container scanning,
image signing, and a policy gate that blocks the merge on high/critical
findings.
