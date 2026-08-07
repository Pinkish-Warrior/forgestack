# vulnerable-app

Functionally identical to [`secure-app`](../secure-app) — same auth, file
upload, and notes endpoints. The difference is three flaws planted on
purpose, so the two apps can be run through the same pipeline and produce
different outcomes.

## Intentional flaws

| # | Flaw | Where | Impact |
|---|---|---|---|
| 1 | SQL injection | `src/app.py` — `GET /notes/search`, `q` param spliced into the query with an f-string instead of a bound parameter | Any authenticated user can exfiltrate **every** user's data, including password hashes, via a UNION-based payload — bypasses the per-user note isolation entirely. Example: `GET /notes/search?q=zzz' UNION SELECT id, username, password_hash FROM users -- ` |
| 2 | Hardcoded secret | `src/app.py` — `SECRET_KEY = "supersecret123"` | `SECRET_KEY` signs Flask session cookies. Anyone who reads the source (public repo) can forge a validly-signed session for any `user_id` — full authentication bypass, no password needed. |
| 3 | Outdated dependency (known CVE) | `requirements.txt` — `Werkzeug==3.0.1` | Vulnerable to CVE-2024-34069 (Werkzeug debugger RCE), fixed in 3.0.3. Flagged by dependency/container scanning (Trivy). |
| 4 | Insecure Dockerfile | `Dockerfile` | `FROM python:latest` (unpinned — image contents drift silently over time); no `USER` directive, so the process runs as `root` inside the container (verified: `uid=0`). |

See [`secure-app/README.md`](../secure-app/README.md) for the fixed
equivalent of each flaw.

## ⚠️ Disclaimer

Intentionally vulnerable, for educational/demo purposes only. Do not deploy
publicly or reuse in production.
