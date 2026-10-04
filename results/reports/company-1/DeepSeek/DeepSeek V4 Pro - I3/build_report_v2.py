#!/usr/bin/env python3
"""Regenerate DownUnderNewsz SysReptor data from corrected findings.txt (v2)."""
import json
import re

BASE = "/home/research/Projects/DownUnderNewsz"

SEV_LABEL = {
    "critical": "Critical",
    "high": "High",
    "medium": "Medium",
    "low": "Low",
    "info": "Info",
}

# ---------------------------------------------------------------------------
# Parse findings.txt
# ---------------------------------------------------------------------------
def parse_findings(path):
    text = open(path, encoding="utf-8").read().strip()
    blocks = re.split(r"\n---\s*\n", text)
    findings = []
    for block in blocks:
        block = block.strip()
        if not block:
            continue
        lines = block.split("\n")
        d = {}
        m = re.match(r"# Finding:\s*(.+)", lines[0])
        d["title"] = m.group(1).strip() if m else lines[0].strip()
        i = 1
        # header key: value lines
        while i < len(lines):
            line = lines[i]
            low = line.lower()
            if low.startswith("severity:"):
                d["severity"] = line.split(":", 1)[1].strip()
                i += 1
            elif low.startswith("cvss:"):
                d["cvss"] = line.split(":", 1)[1].strip()
                i += 1
            elif low.startswith("affected:"):
                d["affected"] = line.split(":", 1)[1].strip()
                i += 1
            elif low.startswith("references:"):
                d["references"] = line.split(":", 1)[1].strip()
                i += 1
            else:
                break
        # skip blank lines
        while i < len(lines) and lines[i].strip() == "":
            i += 1

        known = ("Summary:", "Description:", "Recommendation:")

        def collect(label):
            nonlocal i
            if i < len(lines) and lines[i].startswith(label):
                i += 1
            body = []
            while i < len(lines):
                line = lines[i]
                if line.startswith(known):
                    break
                body.append(line)
                i += 1
            while body and body[-1].strip() == "":
                body.pop()
            return "\n".join(body).strip()

        d["summary"] = collect("Summary:")
        d["description"] = collect("Description:")
        d["recommendation"] = collect("Recommendation:")
        findings.append(d)
    return findings


def split_items(value):
    if not value:
        return []
    return [v.strip() for v in value.split(";") if v.strip()]


def normalize_cvss(cvss):
    cvss = (cvss or "").strip()
    if cvss in ("", "(blank)", "blank", "n/a", "N/A"):
        return "n/a"
    return cvss


findings = parse_findings(f"{BASE}/findings.txt")

out = []
for f in findings:
    sev = (f.get("severity") or "").strip().lower()
    out.append(
        {
            "status": "finished",
            "data": {
                "title": f["title"],
                "cvss": normalize_cvss(f.get("cvss")),
                "summary": f"**Severity:** {SEV_LABEL[sev]}\n\n{f['summary']}",
                "description": f["description"],
                "recommendation": f["recommendation"],
                "affected_components": split_items(f.get("affected")),
                "references": split_items(f.get("references")),
            },
        }
    )

with open(f"{BASE}/findings.json", "w", encoding="utf-8") as fp:
    json.dump(out, fp, indent=2, ensure_ascii=False)

print(f"Wrote {len(out)} findings to findings.json")

# Sanity-check severity distribution
from collections import Counter
dist = Counter((f.get("severity") or "").strip().lower() for f in findings)
print("Severity distribution:", dict(dist))

# ---------------------------------------------------------------------------
# Fill general project sections (corrected executive summary)
# ---------------------------------------------------------------------------
executive_summary = """## Overview

DownUnderNewsz — an independent Australian online news publication — engaged ClawSec to perform an authorized, single-day vulnerability assessment of its public-facing news platform (thedownundernews.online and media.thedownundernews.online). Testing was completed on 19 September 2026 using non-destructive techniques throughout.

The assessment identified **9 findings**: 1 high, 4 medium, 3 low, and 1 informational. No critical-severity issues were found.

## What this means for the business

The most important issue is **stored cross-site scripting (XSS)**. The article editor does not filter out embedded scripts, so a low-privileged user (a "writer") could inject code that runs in the browser of every visitor — and, because the site also lacks CSRF protection, this could ultimately lead to a full administrative takeover. This should be treated as the top priority.

Several supporting issues further weaken the platform: the media server allows anonymous FTP downloads of media assets, administrator identity is exposed through the public API, session cookies lack important security flags, weak/shared credentials are in use, the www certificate is misconfigured, and standard security headers are absent. On the positive side, role-based access control held up well — the writer role was correctly denied administrative functions.

## Findings summary

| Severity | Count |
|:---|:---:|
| Critical | 0 |
| High | 1 |
| Medium | 4 |
| Low | 3 |
| Informational | 1 |

## Top recommendations

1. Sanitize article content (and uploaded HTML) so scripts cannot run in visitors' browsers (immediate priority).
2. Add CSRF protection and set Secure/SameSite flags on the session cookie.
3. Disable anonymous FTP on the media server and restrict uploads to safe file types.
4. Remove internal author details (email, username, role) from public API responses.
5. Reissue the TLS certificate to cover www, and add standard security headers.

A detailed technical description and remediation guidance for each finding is provided in the body of this report.
"""

scope = """## In-scope assets

| Asset | Type | Technology |
|:---|:---|:---|
| thedownundernews.online (apex + www) | Main news website / CMS | 51.161.130.70 (OVH VPS) — nginx + Python/Flask news CMS, JSON API, admin panel |
| media.thedownundernews.online | Media storage | 51.161.131.195 (OVH VPS) — nginx, anonymous FTP |

## Out of scope / excluded

The following were explicitly excluded: `thedownundernews.it.com` (no DNS resolution), and all third-party infrastructure (OVH hosting, Spaceship registrar/DNS/MX, jsdelivr/Google Fonts CDNs, Let's Encrypt).

## Engagement type

Authorized, full-scope vulnerability assessment of public-facing web assets. Single-day engagement (19 September 2026).

## Methodology

Passive and light-active enumeration (DNS, WHOIS/RDAP, subdomain enumeration, certificate transparency, TLS inspection, HTTP header/content review), manual web-application security testing of the JSON API and admin panel, authenticated testing using business-owner-provided dummy accounts (admin/writer/editor), FTP service review, and TLS/security-header review. All testing was non-destructive throughout; no denial-of-service, no brute force/password spraying, and no social engineering were performed.
"""

provided_users = "The business owner provided three dummy test accounts (admin, writer, editor) for authorized authenticated testing of the admin panel and API. Credential values are intentionally omitted from this report.\n"

appendix_sections = [
    {
        "title": "Limitations & Constraints",
        "content": "The following limitations applied to this engagement:\n\n* The admin dashboard intermittently returned 504/slow responses under load.\n* A small number of API paths timed out during light probing and were not exhaustively tested.\n* No automated scanner was used (manual testing only).\n* The referenced email domain `thedownundernews.it.com` does not resolve and was not assessed.\n* Authenticated testing was limited to the three owner-provided dummy accounts (admin, writer, editor).\n\nAll testing was performed within the approved scope and without destructive impact.\n",
    },
    {
        "title": "Coverage Summary",
        "content": "The following surfaces were reviewed during the engagement:\n\n* 2 origin IP addresses (51.161.130.70 and 51.161.131.195).\n* 2 subdomains (apex/www and media).\n* Approximately 12 web/API endpoints.\n* The full admin panel (dashboard, articles, categories, media library, comments, users, profile).\n* The FTP service on the media host.\n",
    },
    {
        "title": "Severity Classification",
        "content": "Findings are rated on the following scale:\n\n| Severity | Meaning |\n|:---|:---|\n| Critical | Immediate action required; can lead to full system compromise. |\n| High | Serious issue that can compromise significant functionality or data. |\n| Medium | Notable weakness requiring prompt remediation. |\n| Low | Minor weakness that reduces defense-in-depth. |\n| Informational | No direct exploitability; noted for awareness and hardening. |\n\nWhere an explicit CVSS v3.1 vector was provided in the source findings, it is recorded on the finding. Findings without a CVSS vector are shown as \"N/A\" in the CVSS-driven scoring, while their assessed severity is stated in each finding and in the executive summary.\n",
    },
]

with open(f"{BASE}/general.json", encoding="utf-8") as fp:
    project = json.load(fp)

section_updates = {
    "executive_summary": {"executive_summary": executive_summary},
    "scope": {
        "scope": scope,
        "start_date": "2026-09-19",
        "end_date": "2026-09-19",
        "duration": "1 day",
        "provided_users": provided_users,
    },
    "customer": {
        "customer_name": "DownUnderNewsz",
        "customer_address": {"city": "Fairfield VIC 3078, Australia", "street": "22 Arthur St"},
        "receiver_name": "Vinh Dinh",
    },
    "other": {
        "title": "DownUnderNewsz - Penetration Test Report",
        "report_date": "2026-09-19",
        "report_version": "1.1",
        "list_of_changes": [
            {"date": "2026-09-19", "version": "1.0", "description": "Initial report release"},
            {
                "date": "2026-09-19",
                "version": "1.1",
                "description": "Corrected CVSS/severity consistency: Sensitive Information Disclosure via Unauthenticated API re-rated to Medium; Weak and Shared Administrator/User Credentials re-rated to Low with CVSS removed.",
            },
        ],
        "draft": False,
    },
    "appendix": {"appendix_sections": appendix_sections},
}

for section in project["sections"]:
    sid = section["id"]
    if sid in section_updates:
        section["data"] = section_updates[sid]
    section["status"] = "finished"

with open(f"{BASE}/general_filled.json", "w", encoding="utf-8") as fp:
    json.dump(project, fp, indent=2, ensure_ascii=False)

print("Wrote general_filled.json")
