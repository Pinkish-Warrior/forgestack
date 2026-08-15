# Walkthrough — running this repo yourself

A from-scratch guide for anyone who's just cloned this repo and wants it
running locally, not just narrated in the README. Every command below was
run for real against this repo before being written down here.

## Prerequisites

- **Python 3** (stdlib only — the exploit script has no pip dependencies).
- **Podman or Docker**, for the container path (recommended — see below).
- **`make`** — ships by default on macOS and most Linux distros.

## The fast path: `make demo`

```bash
make demo
```

This builds both apps, runs them as containers on `localhost:5100`
(`vulnerable-app`) and `localhost:5101` (`secure-app`), fires the same
SQL injection payload at both via
[`security/exploits/sqli_exploit.py`](security/exploits/sqli_exploit.py),
prints the contrast, then tears the containers down. Exit code `0` means
the contrast was confirmed as expected (vulnerable-app leaked rows,
secure-app didn't) — that's the same script and same result behind the
GIF in the README.

Other targets:

```bash
make demo-up    # build + start both apps, leave them running
make demo-down  # stop and remove the demo containers
make help       # list targets
```

`make demo-up` auto-detects Podman or Docker (prefers Podman if both are
installed) — you don't need to know or care which one you have.

## The manual path

If you want to see each step instead of running one command:

```bash
# from the repo root

# 1. Build both images
podman build -t forgestack-vulnerable applications/vulnerable-app
podman build -t forgestack-secure applications/secure-app

# 2. Run both — on 5100/5101, not 5000/5001 (see Gotchas below)
podman run -d --name forgestack-vuln-demo -p 5100:5000 \
  forgestack-vulnerable
podman run -d --name forgestack-secure-demo -p 5101:5000 \
  -e SECRET_KEY="$(openssl rand -hex 32)" \
  forgestack-secure

# 3. Run the exploit against both
python3 security/exploits/sqli_exploit.py --compare \
  --insecure-url http://localhost:5100 \
  --secure-url http://localhost:5101

# 4. Clean up
podman rm -f forgestack-vuln-demo forgestack-secure-demo
```

Swap `podman` for `docker` if that's what you have — both engines produce
standard OCI images, so every command above is identical either way.

This is the same recipe documented (with more narrative) in
[`docs/attack-demo.md`](docs/attack-demo.md), and the literal one VHS runs
to record the demo GIF is [`docs/attack-demo.tape`](docs/attack-demo.tape).

## Running a single app without containers

For poking at one app's code directly — not for the side-by-side
comparison, see the gotcha below:

```bash
cd applications/vulnerable-app   # or applications/secure-app
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python src/app.py
```

`secure-app` additionally needs `SECRET_KEY` set first:

```bash
SECRET_KEY="$(openssl rand -hex 32)" python src/app.py
```

Verified working: a fresh venv, `pip install`, and `create_app()` all
succeed against both apps' real `requirements.txt`.

## Gotchas

- **Both apps hardcode port 5000** (`app.run(port=5000)` in source) — not
  configurable via environment variable. Two consequences:
  - You can't run both apps un-containerized at the same time on one
    machine; they'll fight over the same port. The container path maps
    each to a different host port (5100/5101) precisely to route around
    this, so use it for anything that needs both apps up together.
  - **macOS: port 5000 is unusable** — the AirPlay Receiver service squats
    on it. This affects the un-containerized path even for a single app.
    Either disable AirPlay Receiver in System Settings, or containerize
    and map to 5100/5101 like everything else in this repo does.
- **`secure-app` refuses to start without `SECRET_KEY`** —
  `RuntimeError: SECRET_KEY environment variable must be set`. That's
  intentional: it's the fix for `vulnerable-app`'s hardcoded-secret flaw,
  not a bug. `vulnerable-app` has no such requirement, since its secret is
  hardcoded in source (that's the flaw).
- **Neither app resets its database between runs.** The exploit script
  generates a fresh random victim/attacker username pair every run, so
  re-running it won't error out — but old rows persist, so the leaked row
  count in `make demo`'s output grows on repeat runs against the same
  long-lived containers. That's cumulative test data, not a changing
  vulnerability. `make demo` tears containers down after each run, so a
  fresh `make demo` always starts from an empty database.
- **Container engine case sensitivity**: if you ever build and push these
  images yourself (rather than just running them locally), GHCR requires
  lowercase image names, but Cosign's `certificate-identity-regexp` needs
  the repo's real case (`Pinkish-Warrior/forgestack`) — that's what's
  embedded in the GitHub OIDC certificate. Only relevant if you're
  touching `.github/workflows/secure-pipeline.yml`, not for running the
  demo locally.

## What you can't run locally

The actual CI pipelines (`.github/workflows/insecure-pipeline.yml`,
`secure-pipeline.yml`) run in GitHub Actions on push/PR — they're not
meant to be run locally end-to-end. What you *can* do locally:

- Run Semgrep/Trivy/Gitleaks yourself against either app (same configs
  the pipeline uses, under `security/`) — see
  [`reports/sample-findings.md`](reports/sample-findings.md) for what a
  real local run against `vulnerable-app` found.
- Read [`docs/architecture.md`](docs/architecture.md) for the actual job
  graph, pulled directly from the workflow YAML.
- See a real pipeline run block a real PR: [PR #5](https://github.com/Pinkish-Warrior/forgestack/pull/5)
  (closed unmerged, kept as permanent evidence) reintroduced the SQLi
  into `secure-app` on a throwaway branch and got blocked for real.

## Where to go next

- [`README.md`](README.md) — the pitch, the ELI5, current status.
- [`docs/attack-demo.md`](docs/attack-demo.md) — full exploit write-up.
- [`docs/architecture.md`](docs/architecture.md) — pipeline diagram + proof.
- [`MAPPING.md`](MAPPING.md) — the build plan this repo followed.
