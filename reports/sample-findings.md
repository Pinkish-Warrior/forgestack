# Security Findings Report

Generated: 2026-08-09T08:48:24Z

_Committed sample, generated locally against `applications/vulnerable-app`
(Semgrep, Trivy filesystem, Gitleaks — real runs, not fabricated output).
Scanned the vulnerable app rather than the secure one so the report has
something to show: `secure-app` is clean by design, and this is meant to
demonstrate what the report looks like when there are real findings.
Every PR into `main` generates the same report automatically via the
`findings-report` job in `.github/workflows/secure-pipeline.yml`, scanning
`secure-app` (plus CodeQL and a container image scan, not run locally
here) — see that workflow for the live version. The findings below
correspond to 3 of `vulnerable-app`'s 4 documented intentional flaws
(SQLi, hardcoded secret, CVE-bearing dependency); the fourth
(insecure Dockerfile) isn't caught by these particular tools._

## Summary

| Tool | Findings | Suppressed |
|---|---|---|
| SAST (Semgrep) | 4 | 0 |
| Dependency scan (Trivy) | 1 | 0 |
| Secrets scan (Gitleaks) | 0 | 0 |

## SAST (Semgrep)

| Severity | Rule | Location | Message |
|---|---|---|---|
| HIGH | `security.semgrep.sql-injection-string-formatting` | `applications/vulnerable-app/src/app.py:127` | SQL query built via f-string/string interpolation instead of a parameterized query. User input reaching this pattern can alter the query structure (SQL injection). Use `?`/`%s` placeholders and pass values as execute() parameters instead. |
| HIGH | `python.flask.security.audit.hardcoded-config.avoid_hardcoded_config_SECRET_KEY` | `applications/vulnerable-app/src/app.py:18` | Hardcoded variable `SECRET_KEY` detected. Use environment variables or config files instead |
| HIGH | `security.semgrep.hardcoded-flask-secret-key` | `applications/vulnerable-app/src/app.py:18` | Flask SECRET_KEY assigned a hardcoded string literal instead of being read from the environment. Anyone with source access can forge signed session cookies (full authentication bypass). |
| MEDIUM | `python.flask.security.audit.app-run-param-config.avoid_app_run_with_bad_host` | `applications/vulnerable-app/src/app.py:156` | Running flask app with host 0.0.0.0 could expose the server publicly. |

## Dependency scan (Trivy)

| Severity | Rule | Location | Message |
|---|---|---|---|
| HIGH | `CVE-2024-34069` | `requirements.txt:4` | Package: Werkzeug Installed Version: 3.0.1 Vulnerability CVE-2024-34069 Severity: HIGH Fixed Version: 3.0.3 Link: [CVE-2024-34069](https://avd.aquasec.com/nvd/cve-2024-34069) |

## Secrets scan (Gitleaks)

No findings.
