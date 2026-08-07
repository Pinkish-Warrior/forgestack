# References

Background reading for the security concepts and tooling this project applies.

## SAST vs DAST

- [OWASP Testing Guide](https://owasp.org/www-project-web-security-testing-guide/) — the standard reference for how security testing categories (SAST, DAST, IAST, SCA) fit together and what each catches vs. misses. Good conceptual starting point.
- [OWASP DevSecOps Guideline](https://owasp.org/www-project-devsecops-guideline/) — maps these testing types onto actual pipeline stages, directly relevant to what `secure-pipeline.yml` does here.
- Tool docs become the real teacher once you're hands-on: [Semgrep docs](https://semgrep.dev/docs/) and [CodeQL docs](https://codeql.github.com/docs/) for SAST; [OWASP ZAP docs](https://www.zaproxy.org/docs/) for DAST — ZAP is the free tool most people reach for first.
- [PortSwigger Web Security Academy](https://portswigger.net/web-security) — if you want the DAST side hands-on (attacking a running app rather than reading source), it's free and lab-based.

**Note:** DAST is not currently in this project's scope. `MAPPING.md`'s
Phase 2 covers SAST (Semgrep, CodeQL) plus dependency/container scanning
(Trivy) and image signing (Cosign) — no DAST tooling is wired into either
pipeline. The "Attack vs Defence Pipeline" idea in `PORTFOLIO_OPTIONS.md`
(ZAP/Nikto/sqlmap) is a separate, unbuilt project idea living outside this
repo, not part of ForgeStack.
