
# MAPPING.md — DevSecOps Playground: Structural Development Plan

Project selected: **Option 4, DevSecOps Playground** (see `PORTFOLIO_OPTIONS.md`).
Target: portfolio-ready, finishable in 2–3 weeks.

## 1. Goal

Demonstrate the difference security tooling makes by running the *same*
application through two pipelines — one that catches vulnerabilities before
deploy, one that doesn't — and proving it with a real exploit.

## 2. Repository Structure

```text
ForgeStack/
├── README.md                      # Project pitch, architecture diagram, demo GIF
├── MAPPING.md                     # This file
│
├── applications/
│   ├── vulnerable-app/
│   │   ├── src/                   # SQLi, hardcoded secret, insecure Dockerfile
│   │   ├── Dockerfile             # root user, unpinned base image
│   │   └── README.md              # lists the intentional flaws, for reviewers
│   └── secure-app/
│       ├── src/                   # same features, parameterized queries, env-based secrets
│       ├── Dockerfile             # non-root user, pinned + slim base image
│       └── README.md
│
├── pipelines/                     # human-readable pipeline definitions/docs
│   ├── insecure-pipeline/
│   │   └── README.md              # build → deploy, no gates
│   └── secure-pipeline/
│       └── README.md              # build → SAST → secrets → deps → container → sign → gate → deploy
│
├── .github/workflows/             # actual runnable CI (GitHub Actions requires this path)
│   ├── insecure-pipeline.yml
│   └── secure-pipeline.yml
│
├── security/
│   ├── trivy/trivy-config.yaml        # dependency + container image scan config
│   ├── semgrep/semgrep-rules.yaml     # SAST rules
│   ├── codeql/codeql-config.yml       # GitHub-native SAST
│   └── cosign/cosign-policy.yaml      # image signing + verification policy
│
├── reports/
│   └── sample-findings.md         # example generated report, committed for reviewers
│
└── docs/
    ├── architecture.md            # diagram + narrative
    └── attack-demo.md             # exact exploit steps used to prove the contrast
```

**Note:** `pipelines/` holds the readable/documented version of each pipeline;
the executable GitHub Actions YAML lives in `.github/workflows/` because
that's the only path GitHub will actually run. `pipelines/*/README.md`
cross-links to the real workflow file so the repo layout stays intuitive
for reviewers while remaining functional.

## 3. Build Phases

### Phase 1 — Applications (Days 1–5)
| Day | Task |
|---|---|
| 1 | Pick stack, scaffold `vulnerable-app` (auth + file upload + DB-backed endpoint) |
| 2 | Inject flaws: SQLi, hardcoded secret, outdated CVE-bearing dependency |
| 3 | Insecure Dockerfile (root user, unpinned tags) |
| 4 | Build `secure-app` — same features, hardened equivalents |
| 5 | Verify both apps run identically; write per-app README listing the flaw/fix pairs |

### Phase 2 — Pipelines & Security Tooling (Days 6–10)
| Day | Task |
|---|---|
| 6 | `insecure-pipeline.yml`: build → deploy, no scanning |
| 7 | `secure-pipeline.yml` skeleton: build stage + deploy stage |
| 8 | Wire in Semgrep (SAST) + secrets scan |
| 9 | Wire in Trivy (dependency + container scan) + CodeQL |
| 10 | Wire in Cosign (image signing) + policy gate that fails build on high/critical findings |

### Phase 3 — Proof & Polish (Days 11–15)
| Day | Task |
|---|---|
| 11 | Script the exploit (e.g. SQLi payload) against both deployed apps |
| 12 | Run insecure pipeline → confirm vuln ships; run secure pipeline → confirm it's blocked |
| 13 | Auto-generate findings report (SARIF → `reports/` markdown/HTML summary) |
| 14 | Record before/after GIF; write `docs/architecture.md` + `docs/attack-demo.md` |
| 15 | Final README pass — lead with the contrast, not the tool list |

## 4. Decisions

- **App stack**: ✅ Python/Flask — chosen for readability of the vulnerable/secure
  diff, single-language app + exploit script, and alignment with security tooling.
- **CI provider**: GitHub Actions (implied by `codeql/` in the layout —
  CodeQL is GitHub-native).
- **Container runtime**: engine-agnostic — must build and run identically under
  both Docker and Podman (author's local machine has Podman only; reviewers
  can't be assumed to have either specifically). CI uses Docker (GitHub-hosted
  runners ship with it preinstalled); local dev uses Podman. To guarantee both
  work without divergence:
  - Keep `Dockerfile` to vanilla, spec-standard syntax — no BuildKit-only
    features (e.g. `--mount=type=secret`, `# syntax=` directives) that Podman
    doesn't support identically.
  - If a compose file is added, name it `compose.yaml` (engine-neutral) and
    stick to common compose-spec fields only — both `docker compose` and
    `podman compose` read the same file.
  - Never hardcode `docker` in scripts/README commands — either document both
    (`docker build ...` / `podman build ...`) or add a tiny wrapper that
    auto-detects which is installed.
  - Both engines produce standard OCI images, so Trivy/Cosign behave
    identically regardless of which one built the image.
  - This constraint applies starting Phase 1, Day 3 (first Dockerfile) —
    nothing to verify yet.
- **Deploy target for the demo**: local Compose (via `podman compose` or
  `podman-compose`) is enough to prove the contrast; a live deploy (e.g. small
  cloud instance) adds credibility but isn't required for the 2–3 week scope.
- **Branching strategy**: all work happens on `dev`, merged into `main` via
  pull request — never commit directly to `main`. Once `secure-pipeline.yml`
  exists (Phase 2), it must be a required check on PRs into `main`, so a PR
  with a high/critical finding shows a blocked merge. This isn't just process
  ceremony — it's the same gate the project is demonstrating, applied to its
  own repo, and doubles as a portfolio screenshot (a red X blocking a PR).
  `main` should only ever contain commits that passed the gate.

## 5. Definition of Done

- Both apps run and are functionally identical.
- Insecure pipeline visibly ships the vulnerability; secure pipeline visibly blocks it.
- One committed sample report in `reports/`.
- README tells the story in under 60 seconds of reading.
