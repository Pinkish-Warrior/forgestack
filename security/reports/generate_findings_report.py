#!/usr/bin/env python3
"""Merge one or more SARIF files into a single human-readable Markdown
findings report. Stdlib only -- runs on any GitHub-hosted runner or dev
machine with no extra install step.

Usage:
    generate_findings_report.py --output reports/findings-report.md \
        --input "SAST (Semgrep)=semgrep.sarif" \
        --input "Dependency scan (Trivy)=trivy-fs.sarif"

Each --input is "Label=path/to/file.sarif". The label is what's shown as
the section heading -- explicit rather than derived from the SARIF tool
name, since two inputs (e.g. Trivy filesystem vs image scan) can share the
same underlying tool but need to stay distinct in the report.
"""

import argparse
import datetime
import json
import sys
from pathlib import Path

# SARIF "level" -> a reader-friendly severity label. SARIF itself doesn't
# have a single canonical severity field (levels are about result kind,
# not risk), but every scanner this project uses maps its real severity
# onto "error"/"warning"/"note" in practice, so this is a reasonable
# normalization for a summary table rather than reproducing five
# different tools' own severity vocabularies.
LEVEL_LABELS = {
    "error": "HIGH",
    "warning": "MEDIUM",
    "note": "LOW",
    "none": "INFO",
}
LEVEL_ORDER = {"error": 0, "warning": 1, "note": 2, "none": 3}


def load_findings(path):
    data = json.loads(Path(path).read_text())
    findings = []
    for run in data.get("runs", []):
        rules_by_id = {
            rule.get("id"): rule
            for rule in run.get("tool", {}).get("driver", {}).get("rules", [])
        }
        for result in run.get("results", []):
            rule_id = result.get("ruleId", "unknown")
            level = result.get("level")
            if not level:
                rule = rules_by_id.get(rule_id, {})
                level = rule.get("defaultConfiguration", {}).get("level", "warning")

            message = result.get("message", {}).get("text", "").strip()
            message = " ".join(message.split())  # collapse newlines/whitespace

            location = "-"
            locations = result.get("locations") or []
            if locations:
                phys = locations[0].get("physicalLocation", {})
                uri = phys.get("artifactLocation", {}).get("uri", "?")
                line = phys.get("region", {}).get("startLine")
                location = f"{uri}:{line}" if line else uri

            findings.append(
                {
                    "rule_id": rule_id,
                    "level": level,
                    "severity": LEVEL_LABELS.get(level, level.upper()),
                    "location": location,
                    "message": message or "(no message)",
                }
            )

    findings.sort(key=lambda f: (LEVEL_ORDER.get(f["level"], 9), f["location"]))
    return findings


def render_section(label, findings):
    lines = [f"## {label}", ""]
    if not findings:
        lines += ["No findings.", ""]
        return lines

    lines += ["| Severity | Rule | Location | Message |", "|---|---|---|---|"]
    for f in findings:
        message = f["message"].replace("|", "\\|")
        lines.append(
            f"| {f['severity']} | `{f['rule_id']}` | `{f['location']}` | {message} |"
        )
    lines.append("")
    return lines


def render_report(labeled_findings, generated_at):
    lines = [
        "# Security Findings Report",
        "",
        f"Generated: {generated_at}",
        "",
        "## Summary",
        "",
        "| Tool | Findings |",
        "|---|---|",
    ]
    for label, findings in labeled_findings:
        lines.append(f"| {label} | {len(findings)} |")
    lines.append("")

    for label, findings in labeled_findings:
        lines += render_section(label, findings)

    return "\n".join(lines).rstrip() + "\n"


def parse_input(raw):
    if "=" not in raw:
        raise argparse.ArgumentTypeError(
            f"--input must be LABEL=PATH, got: {raw!r}"
        )
    label, path = raw.split("=", 1)
    return label, path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input",
        action="append",
        type=parse_input,
        required=True,
        dest="inputs",
        metavar="LABEL=PATH",
        help="A labeled SARIF file. Repeatable.",
    )
    parser.add_argument("--output", required=True, help="Path to write the report to.")
    args = parser.parse_args()

    generated_at = datetime.datetime.now(datetime.timezone.utc).strftime(
        "%Y-%m-%dT%H:%M:%SZ"
    )

    labeled_findings = []
    for label, path in args.inputs:
        if not Path(path).exists():
            print(f"warning: {path} not found, skipping {label}", file=sys.stderr)
            labeled_findings.append((label, []))
            continue
        labeled_findings.append((label, load_findings(path)))

    report = render_report(labeled_findings, generated_at)
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(report)
    print(f"wrote {args.output}")


if __name__ == "__main__":
    main()
