ENGINE := $(shell command -v podman 2>/dev/null || command -v docker 2>/dev/null)

VULN_PORT ?= 5100
SECURE_PORT ?= 5101
VULN_NAME := forgestack-vuln-demo
SECURE_NAME := forgestack-secure-demo

.PHONY: help demo demo-build demo-up demo-down

help:
	@echo "make demo       - build + run both apps, run the SQLi exploit against both, tear down"
	@echo "make demo-up    - build + run both apps, leave them running on :$(VULN_PORT) / :$(SECURE_PORT)"
	@echo "make demo-down  - stop and remove the demo containers"

demo-build:
	@if [ -z "$(ENGINE)" ]; then \
		echo "Error: no container engine found on PATH (install podman or docker)" >&2; \
		exit 1; \
	fi
	$(ENGINE) build -t forgestack-vulnerable applications/vulnerable-app
	$(ENGINE) build -t forgestack-secure applications/secure-app

demo-up: demo-build
	-@$(ENGINE) rm -f $(VULN_NAME) $(SECURE_NAME) >/dev/null 2>&1
	$(ENGINE) run -d --name $(VULN_NAME) -p $(VULN_PORT):5000 \
		forgestack-vulnerable
	$(ENGINE) run -d --name $(SECURE_NAME) -p $(SECURE_PORT):5000 \
		-e SECRET_KEY="$$(openssl rand -hex 32)" \
		forgestack-secure
	@echo "Waiting for both apps to come up..."
	@sleep 2
	@echo "vulnerable-app: http://localhost:$(VULN_PORT)   secure-app: http://localhost:$(SECURE_PORT)"

demo-down:
	-@$(ENGINE) rm -f $(VULN_NAME) $(SECURE_NAME) >/dev/null 2>&1

demo: demo-up
	@echo
	@echo "Running the SQLi exploit against both apps..."
	@echo
	@python3 security/exploits/sqli_exploit.py --compare \
		--insecure-url http://localhost:$(VULN_PORT) \
		--secure-url http://localhost:$(SECURE_PORT); \
	status=$$?; \
	$(MAKE) --no-print-directory demo-down; \
	exit $$status
