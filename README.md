# ForgeStack — DevSecOps Playground

> **TL;DR:** Same app, two assembly lines. One ships bugs to production. The other catches them before they leave the factory. This repo proves it with a real exploit — same attack, run against both, different outcomes.

![Same SQLi payload run against vulnerable-app and secure-app — vulnerable-app leaks rows including password hashes, secure-app returns nothing](docs/attack-demo.gif)

Full write-up and reproduction steps: [`docs/attack-demo.md`](docs/attack-demo.md).

---

## ELI5

Imagine two toy-car factories building the exact same car.

- **Factory A** slaps the car together and ships it straight out the door. No inspection.
- **Factory B** runs every car through a checklist first — checking the brakes, checking the wiring, checking nothing's loose — before it's allowed to leave.

Both factories *look* like they're doing the same job. The only way to know Factory B is actually better is to watch what happens when a car has something wrong with it.

That's what this repo does, except instead of toy cars, it's a small web app — and instead of "something wrong," it's four real, intentionally-planted security bugs:

1. **A SQL injection hole** — think of it like a form on a website that, instead of just accepting your name, will also accept sneaky commands and hand over the whole database if you type the right trick.
2. **A hardcoded secret** — like taping your house key to the front door where anyone can find it, instead of keeping it somewhere safe.
3. **An outdated ingredient with a known recall** — a dependency version with a publicly documented bug, kept in use even though a fixed version already exists.
4. **A wide-open front door** — the container runs as an all-powerful root user, and its base image isn't locked to a specific, reviewed version, so what actually ships can silently change underneath you.

There are **two versions of the same app**:
- `vulnerable-app` — has all four bugs, on purpose.
- `secure-app` — same features, all four fixed properly.

And **two pipelines** (the automated "factory line" that builds and deploys the code):
- **Insecure pipeline** — build → deploy. No checks. Anything goes.
- **Secure pipeline** — build → five parallel scans → sign → verify → *then* deploy. If something's wrong, it stops before it ever reaches production.

The secure pipeline uses five tools as its inspectors, plus a final gate:
| Tool | What it checks, in plain terms |
|---|---|
| [**Semgrep**](https://semgrep.dev/) | Reads the actual code for known-bad patterns (like the SQLi hole) |
| [**CodeQL**](https://codeql.github.com/) | GitHub's own deep code scanner, another set of eyes on the source |
| [**Gitleaks**](https://github.com/gitleaks/gitleaks) | Scans for secrets accidentally committed to source (like the hardcoded key) |
| [**Trivy**](https://trivy.dev/) | Checks the app's ingredients (dependencies) and the container for known vulnerabilities |
| [**Cosign**](https://docs.sigstore.dev/cosign/) | Digitally signs the finished container, like a tamper-evident seal, so you know what shipped is what was checked |

Signing isn't the last word, though — a separate **gate** step then *verifies* that signature before deploy is allowed to run at all. That's the difference between "the scans were configured to run" and "the scans provably ran and passed": the gate won't accept a signature that doesn't check out, and deploy can't get the image any other way.

**The proof:** run the same attack against both. The insecure pipeline lets it through. The secure pipeline blocks the deploy. Side by side, that's the whole story — not "trust me, security tooling helps," but "watch it happen."

---

## Why this exists

This is a portfolio project built to demonstrate hands-on DevSecOps skills — not just knowing the tool names, but wiring them into a real CI/CD gate that actually fails a build when it should. `main` enforces this for real: all 10 pipeline checks are required status checks, so a PR with a failing scan can't be merged — not just flagged, actually blocked.

## Structure

```
forgestack/
├── applications/
│   ├── vulnerable-app/    # the bug-ridden version
│   └── secure-app/        # the hardened version
├── pipelines/             # human-readable pipeline docs
├── .github/workflows/     # the actual runnable GitHub Actions
├── security/              # config for Semgrep, Trivy, CodeQL, Cosign
├── reports/                # sample findings report + captured exploit run
└── docs/
    ├── references.md      # background reading (SAST/DAST, tool docs)
    ├── architecture.md    # pipeline diagram + narrative
    ├── attack-demo.md     # exact exploit steps + reproduction
    └── attack-demo.gif    # recorded proof: same attack, both apps
```

## ⚠️ Disclaimer

`vulnerable-app` is intentionally broken for educational/demo purposes. **Do not deploy it publicly or reuse it in production.**

## Status

**Phase 2 (both pipelines, fully gated) is complete.** `insecure-pipeline` and
`secure-pipeline` are both live, and `secure-pipeline` runs all five scans,
signs, and verifies as described above — every part of that is real and
running today, not aspirational.

**Phase 3 (the exploit proof) is done**: the attack is scripted and run
for real against both apps (see the GIF above and
[`docs/attack-demo.md`](docs/attack-demo.md)), the secure pipeline's gate
is verified to actually block a reintroduced vulnerability, every PR gets
an auto-generated findings report ([sample](reports/sample-findings.md)),
and [`docs/architecture.md`](docs/architecture.md) has the pipeline
diagram and the proof behind it. Only remaining: a final README pass
(Day 15).

## References

- [Semgrep](https://semgrep.dev/) — static analysis (SAST) engine used to catch bad code patterns
- [CodeQL](https://codeql.github.com/) — GitHub's semantic code analysis engine
- [Gitleaks](https://github.com/gitleaks/gitleaks) — secrets scanner
- [Trivy](https://trivy.dev/) — vulnerability scanner for dependencies, containers, and IaC
- [Cosign](https://docs.sigstore.dev/cosign/) — container signing and verification (part of [Sigstore](https://www.sigstore.dev/))

For background on SAST vs. DAST and further reading, see [`docs/references.md`](docs/references.md).
