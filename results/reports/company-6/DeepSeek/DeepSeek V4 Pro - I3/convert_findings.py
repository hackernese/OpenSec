#!/usr/bin/env python3
"""Convert findings.txt into reptor finding JSON."""
import json
import re
import sys

path = "/home/research/Projects/AuSecurity/findings.txt"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

blocks = [b.strip() for b in content.split("\n---\n") if b.strip()]

findings = []

for block in blocks:
    lines = block.split("\n")
    data = {}
    # Parse header fields and free-text blocks
    title = None
    severity = ""
    cvss = ""
    affected = ""
    references = []
    summary = []
    description = []
    recommendation = []

    current = None  # which free-text section we're in
    for line in lines:
        if line.startswith("# Finding:"):
            title = line.split("# Finding:", 1)[1].strip()
            current = None
            continue
        if line.startswith("Severity:"):
            severity = line.split("Severity:", 1)[1].strip().lower()
            current = None
            continue
        if line.startswith("CVSS:"):
            cvss = line.split("CVSS:", 1)[1].strip()
            current = None
            continue
        if line.startswith("Affected:"):
            affected = line.split("Affected:", 1)[1].strip()
            current = None
            continue
        if line.startswith("References:"):
            ref = line.split("References:", 1)[1].strip()
            if ref:
                references.append(ref)
            current = None
            continue
        if line.strip() == "Summary:":
            current = "summary"
            continue
        if line.strip() == "Description:":
            current = "description"
            continue
        if line.strip() == "Recommendation:":
            current = "recommendation"
            continue
        # content line
        if current == "summary":
            summary.append(line)
        elif current == "description":
            description.append(line)
        elif current == "recommendation":
            recommendation.append(line)

    # Parse affected components (split on comma)
    affected_components = []
    if affected:
        affected_components = [a.strip() for a in affected.split(",") if a.strip()]

    finding = {
        "status": "finished",
        "data": {
            "title": title,
            "severity": severity,
            "cvss": cvss,
            "summary": "\n".join(summary).strip(),
            "description": "\n".join(description).strip(),
            "recommendation": "\n".join(recommendation).strip(),
            "affected_components": affected_components,
            "references": references,
        },
    }
    findings.append(finding)

with open("/home/research/Projects/AuSecurity/findings.json", "w", encoding="utf-8") as f:
    json.dump(findings, f, indent=2)

print(f"Converted {len(findings)} findings.")
for f in findings:
    print(f"- [{f['data']['severity']}] {f['data']['title']}")
