#!/usr/bin/env python3
"""Parse findings.txt into the SysReptor JSON format."""
import json
import re
import sys

SEVERITY_MAP = {
    "critical": "critical",
    "high": "high",
    "medium": "medium",
    "low": "low",
    "info": "info",
    "informational": "info",
}

def parse_file(path):
    with open(path) as f:
        content = f.read()
    # Split on separator lines
    raw_sections = re.split(r"\n---\s*\n", content)
    findings = []
    for raw in raw_sections:
        raw = raw.strip()
        if not raw:
            continue
        lines = raw.split("\n")
        title = None
        severity = None
        cvss = ""
        affected = ""
        references = ""
        summary_text = ""
        description_text = ""
        recommendation_text = ""
        current_block = None
        header_done = False
        buf = []

        def flush():
            nonlocal buf, current_block, summary_text, description_text, recommendation_text
            text = "\n".join(buf).strip()
            if current_block == "summary":
                summary_text = text
            elif current_block == "description":
                description_text = text
            elif current_block == "recommendation":
                recommendation_text = text
            buf = []

        for line in lines:
            if line.startswith("# Finding:"):
                title = line.split(":", 1)[1].strip()
                continue
            # Section headers
            m = re.match(r"^(Summary|Description|Recommendation):\s*$", line)
            if m:
                flush()
                current_block = m.group(1).lower()
                header_done = True
                continue
            if not header_done:
                # Still parsing header fields
                if line.startswith("Severity:"):
                    severity = line.split(":", 1)[1].strip().lower()
                elif line.startswith("CVSS:"):
                    cvss = line.split(":", 1)[1].strip()
                elif line.startswith("Affected:"):
                    affected = line.split(":", 1)[1].strip()
                elif line.startswith("References:"):
                    references = line.split(":", 1)[1].strip()
                # Blank lines in header ignored
                continue
            # In a body block
            buf.append(line)
        flush()

        # Normalize CVSS
        if cvss:
            m = re.search(r"(CVSS:3\.[01]/[^\s\(\)]+)", cvss)
            if m:
                cvss_val = m.group(1)
            else:
                cvss_val = ""
        else:
            cvss_val = ""

        # Parse affected into list - split on comma or " , "
        affected_list = [a.strip() for a in re.split(r"\s*,\s*", affected) if a.strip()]

        # Parse references - split on comma
        ref_list = [r.strip() for r in re.split(r"\s*,\s*", references) if r.strip()]

        sev = SEVERITY_MAP.get((severity or "").lower(), "info")

        findings.append({
            "status": "finished",
            "data": {
                "title": title,
                "cvss": cvss_val,
                "severity": sev,
                "summary": summary_text,
                "description": description_text,
                "recommendation": recommendation_text,
                "affected_components": affected_list,
                "references": ref_list,
            },
        })
    return findings


if __name__ == "__main__":
    findings = parse_file(sys.argv[1])
    print(json.dumps(findings, indent=2))
    sys.stderr.write(f"Parsed {len(findings)} findings\n")
    counts = {}
    for f in findings:
        counts[f["data"]["severity"]] = counts.get(f["data"]["severity"], 0) + 1
    sys.stderr.write(f"Breakdown: {counts}\n")
