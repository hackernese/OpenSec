#!/usr/bin/env python3
"""Convert findings.txt to SysReptor finding JSON."""
import json
import re
import sys

SEV_MAP = {"critical": "critical", "high": "high", "medium": "medium", "low": "low", "info": "info"}

def parse(path):
    text = open(path).read()
    # Split on separator lines
    chunks = re.split(r"\n---\s*\n", text.strip())
    findings = []
    for chunk in chunks:
        chunk = chunk.strip()
        if not chunk:
            continue
        # Title
        m = re.search(r"^#\s*Finding:\s*(.+?)\s*$", chunk, re.M)
        if not m:
            continue
        title = m.group(1).strip()

        def grab(field):
            r = re.search(rf"^{field}:\s*(.+?)\s*$", chunk, re.M)
            return r.group(1).strip() if r else None

        severity = (grab("Severity") or "info").lower()
        severity = SEV_MAP.get(severity, "info")

        cvss_raw = grab("CVSS") or ""
        # keep only vector string, strip trailing score in parens
        cvss_m = re.search(r"(CVSS:[\d.]+/[A-Z0-9:/]+)", cvss_raw)
        cvss = cvss_m.group(1) if cvss_m else ""

        affected_raw = grab("Affected") or ""
        affected = [a.strip() for a in re.split(r",\s*", affected_raw) if a.strip()]

        # References can be inline or bullet list
        refs = []
        ref_block = re.search(r"^References:\s*\n((?:[-*].+\n?)+)", chunk, re.M)
        if ref_block:
            for line in ref_block.group(1).splitlines():
                item = re.sub(r"^[-*]\s*", "", line).strip()
                if item:
                    refs.append(item)
        else:
            ref_inline = grab("References")
            if ref_inline:
                refs = [r.strip() for r in re.split(r",\s*", ref_inline) if r.strip()]

        def block(name, next_names):
            # Extract multi-line block between "Name:" and next heading
            pattern = rf"^{name}:\s*\n(.*?)(?=^(?:{'|'.join(next_names)}):\s*\n|\Z)"
            m = re.search(pattern, chunk, re.M | re.S)
            if not m:
                return ""
            return m.group(1).strip()

        summary = block("Summary", ["Description", "Evidence", "Recommendation"])
        description = block("Description", ["Evidence", "Recommendation"])
        evidence = block("Evidence", ["Recommendation"])
        recommendation = block("Recommendation", ["Evidence"])

        # Merge evidence (sanitize absolute paths) into description if present
        if evidence:
            # Keep only file basenames to avoid leaking workspace paths
            sanitized = []
            for line in evidence.splitlines():
                line = re.sub(r"^[-*]\s*", "", line).strip()
                if not line:
                    continue
                # replace absolute path with just the final two components
                sanitized.append(f"- {line.split('/')[-2]}/{line.split('/')[-1]}" if "/" in line else f"- {line}")
            description = description + "\n\n**Supporting evidence collected during the engagement:**\n" + "\n".join(sanitized)

        findings.append({
            "status": "finished",
            "data": {
                "title": title,
                "cvss": cvss,
                "summary": summary,
                "description": description,
                "recommendation": recommendation,
                "affected_components": affected,
                "references": refs,
            }
        })
    return findings

if __name__ == "__main__":
    out = parse(sys.argv[1])
    json.dump(out, sys.stdout, indent=2)
