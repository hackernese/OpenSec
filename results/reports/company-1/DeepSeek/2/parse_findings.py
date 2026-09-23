#!/usr/bin/env python3
import json
import re

path = "/home/research/Projects/DownUnderNewsz/findings.txt"
with open(path, "r") as f:
    text = f.read()

# Split into finding blocks on '---' lines
blocks = re.split(r"\n\s*---\s*\n", text)

KNOWN_FIELDS = {
    "Severity", "CVSS", "Affected", "References",
    "Summary", "Description", "Recommendation",
}

findings = []
for block in blocks:
    block = block.strip()
    if not block:
        continue
    lines = block.split("\n")
    title = None
    fields = {}
    current_key = None
    current_buf = []

    def flush():
        if current_key is not None:
            fields[current_key] = "\n".join(current_buf).strip()
        return

    for line in lines:
        if line.startswith("# Finding:"):
            title = line[len("# Finding:"):].strip()
            continue
        m = re.match(r"^([A-Za-z]+):\s?(.*)$", line)
        if m and m.group(1) in KNOWN_FIELDS:
            flush()
            current_key = m.group(1)
            current_buf = [m.group(2)] if m.group(2) else []
        else:
            if current_key is not None:
                current_buf.append(line)
    flush()

    if title is None:
        continue

    cvss = fields.get("CVSS", "").strip()
    affected_raw = fields.get("Affected", "").strip()
    refs_raw = fields.get("References", "").strip()

    # Affected components: split only when two distinct URLs are joined by " and "
    if " and " in affected_raw:
        parts = [p.strip() for p in affected_raw.split(" and ")]
        if all("://" in p for p in parts):
            affected = parts
        else:
            affected = [affected_raw]
    else:
        affected = [affected_raw] if affected_raw else []

    references = refs_raw.split() if refs_raw else []

    def escape_html(s):
        # Escape angle brackets so literal payloads (e.g. <script>) render as
        # plain text instead of being interpreted as HTML by the report engine.
        return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    finding = {
        "status": "finished",
        "data": {
            "title": title,
            "cvss": cvss,
            "summary": escape_html(fields.get("Summary", "")),
            "description": escape_html(fields.get("Description", "")),
            "recommendation": escape_html(fields.get("Recommendation", "")),
            "affected_components": affected,
            "references": references,
        },
    }
    findings.append(finding)

out = "/home/research/Projects/DownUnderNewsz/findings.json"
with open(out, "w") as f:
    json.dump(findings, f, indent=2)

print(f"Parsed {len(findings)} findings -> {out}")
for f in findings:
    d = f["data"]
    print("-", d["title"], "| cvss:", repr(d["cvss"]), "| affected:", d["affected_components"], "| refs:", len(d["references"]))
