#!/usr/bin/env python3
"""Parse findings.txt into reptor finding JSON format."""
import json
import re
import sys

FINDINGS_PATH = "/home/research/Projects/AuSecurity/findings.txt"
OUTPUT_PATH = "/home/research/Projects/AuSecurity/report/findings.json"

def parse_findings(text):
    findings = []
    # Split into blocks on lines that are exactly '---'
    blocks = re.split(r'(?m)^---\s*$', text)
    for block in blocks:
        block = block.strip()
        if not block:
            continue
        # Only process blocks that start with '# Finding:'
        if not block.startswith('# Finding:'):
            continue

        title_match = re.match(r'# Finding:\s*(.*)', block)
        title = title_match.group(1).strip() if title_match else ""

        def field_value(name):
            m = re.search(r'(?m)^' + re.escape(name) + r':[ \t]*(.*)$', block)
            return m.group(1).strip() if m else ""

        def text_block(name):
            # find the block starting at 'Name:' and ending at next known field or end of block
            m = re.search(
                r'(?m)^' + re.escape(name) + r':[ \t]*\n(.*?)'
                r'(?=\n(?:Severity|CVSS|Affected|References|Summary|Description|Recommendation|Precondition|Impact):|\Z)',
                block, re.DOTALL,
            )
            if m:
                return m.group(1).strip()
            return ""

        severity = field_value("Severity").lower()
        cvss = field_value("CVSS")
        affected = field_value("Affected")
        references = field_value("References")
        summary = text_block("Summary")
        description = text_block("Description")
        recommendation = text_block("Recommendation")

        # Build affected_components list: split on ';' where clearly multiple
        if ';' in affected:
            affected_components = [a.strip() for a in affected.split(';') if a.strip()]
        else:
            affected_components = [affected]

        # Build references list: split on ', '
        ref_list = [r.strip() for r in references.split(', ') if r.strip()] if references else []

        finding = {
            "status": "finished",
            "data": {
                "title": title,
                "severity": severity,
                "cvss": cvss,
                "summary": summary,
                "description": description,
                "recommendation": recommendation,
                "affected_components": affected_components,
                "references": ref_list,
            },
        }
        findings.append(finding)
    return findings

def main():
    with open(FINDINGS_PATH, "r", encoding="utf-8") as f:
        text = f.read()
    findings = parse_findings(text)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(findings, f, indent=2, ensure_ascii=False)
    print(f"Parsed {len(findings)} findings -> {OUTPUT_PATH}")
    for fn in findings:
        d = fn["data"]
        print(f"  - [{d['severity']}] {d['title']}")

if __name__ == "__main__":
    main()
