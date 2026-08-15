# Attack demo

![Same SQLi payload run against vulnerable-app and secure-app — vulnerable-app leaks rows including password hashes, secure-app returns nothing](attack-demo.gif)

The GIF above is a real, unedited recording of [`security/exploits/sqli_exploit.py`](../security/exploits/sqli_exploit.py)
run in `--compare` mode: one UNION-based SQL injection payload, sent to both
apps' `GET /notes/search?q=` endpoint back to back.

- **`vulnerable-app`** builds its query by splicing the `q` parameter
  directly into an f-string. The payload rides along and the database
  returns rows it was never meant to — including other users' password
  hashes.
- **`secure-app`** runs the identical feature through a parameterized
  query. The same payload is treated as a literal string, not SQL, so the
  injection has no effect.

Same app, same attack, different outcome — because of what's different in
the code, not because the attack was weakened for the demo.

## Reproduce it yourself

Fastest path: `make demo` from the repo root — see
[`WALKTHROUGH.md`](../WALKTHROUGH.md) for the one-command version and
troubleshooting. The steps below are the same thing spelled out manually.

Requires [Podman](https://podman.io/) (or Docker — see the note on engine
neutrality in [`MAPPING.md`](../MAPPING.md)) and Python 3.

```bash
# from the repo root

# 1. Build both images
podman build -t forgestack-vulnerable applications/vulnerable-app
podman build -t forgestack-secure applications/secure-app

# 2. Run both, on 5100/5101 — not 5000/5001, see gotcha below
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

To regenerate the GIF itself (requires [VHS](https://github.com/charmbracelet/vhs),
`brew install vhs`), start both containers as above, then:

```bash
vhs docs/attack-demo.tape
```

`docs/attack-demo.tape` is the literal script VHS runs — it's the exact
recipe, not just a description of one.

### Gotchas if you're reproducing this

- **`secure-app` requires `SECRET_KEY` to be set** or it refuses to start
  (`RuntimeError: SECRET_KEY environment variable must be set`). That's
  intentional — it's the fix for `vulnerable-app`'s hardcoded secret flaw,
  not a bug. `vulnerable-app` has no such requirement, since its secret is
  hardcoded in source.
- **Local port 5000 is unusable on macOS** — the AirPlay Receiver service
  squats on it. Use 5100/5101 (or disable AirPlay Receiver in System
  Settings) instead of the app's default `5000`/`5001`.
- **The exploit script is safe to run repeatedly** — it generates a fresh
  random victim/attacker username pair (`secrets.token_hex(4)`) on every
  run, so it won't collide with accounts from a previous run. But neither
  app resets its database between runs, so if you run the exploit multiple
  times against the same long-lived containers, the row count in the
  `VULNERABLE:` output grows each time (every prior run's victim/attacker
  rows are still there to leak) — that's cumulative test data, not a
  changing vulnerability.
