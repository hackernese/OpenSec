#!/usr/bin/env python3
"""Fill the exported SysReptor project JSON with corrected engagement details."""
import json

SRC = "/home/research/Projects/AuSecurity/report/general_new.json"
DST = "/home/research/Projects/AuSecurity/report/project_filled_new.json"

executive_summary = """# Executive Summary

Ausecurity is an Australian GRC consulting and penetration-testing firm (CREST Certified, ISO 27001, OSCP). On 17 September 2026, an authorized, full-scope security assessment was performed against its public-facing web estate. The goal was to identify weaknesses an attacker could exploit and to provide practical, prioritized remediation guidance.

## Overall Result

The assessment identified **12 findings** in total: **2 critical**, **2 high**, **4 medium**, **3 low**, and **1 informational**. The most serious issue lets a remote attacker run arbitrary commands on the main web server without logging in. Combined with the other findings, this enables full compromise of the web server and exposure of confidential client information.

## What This Means for the Business

* **Server takeover risk.** A flaw in how the website handles login session data lets an attacker execute commands directly on the server. This is the single highest priority to fix.
* **Weak admin protection.** The administrative portal still accepts the well-known default username and password (`admin` / `admin`), allowing anyone who knows it to sign in.
* **Confidential data exposure.** Once signed in, the admin dashboard displays client names, contact emails, and financial figures. Because access relies on that default password, this data is effectively public today.
* **Unfinished helpdesk.** The customer support system (osTicket) is live but was never fully installed. Anyone could complete the setup wizard and become its administrator before the business does.
* **Additional weaknesses.** Cross-site scripting, an exposed WordPress XML-RPC interface, user and directory enumeration, a self-signed certificate, a missing cookie security flag, an open redirect, and several version disclosures further increase risk.

## Priority Actions

1. Replace the unsafe session handling with signed, tamper-proof sessions (fixes the critical remote-code-execution issue).
2. Change all administrative passwords and enable multi-factor authentication.
3. Complete and secure the osTicket installation, then remove or restrict its setup directory.
4. Disable WordPress XML-RPC and user enumeration, and fix the cross-site scripting and open-redirect issues.
5. Replace the self-signed certificate with a trusted certificate, and disable directory listing and version banners.

Detailed technical findings and remediation steps are provided in the Findings section of this report.

**Contact:** info@ausecurity.best"""

scope = """# Scope

This engagement was a full-scope, authorized vulnerability assessment of Ausecurity's public-facing assets, performed on 17 September 2026.

## In-Scope Assets

| Asset | IP Address |
|:---|---:|
| ausecurity.best (main website, admin login, API backend) | 51.79.166.148 |
| www.ausecurity.best and contact.ausecurity.best | 51.79.166.148 |
| blog.ausecurity.best (WordPress) | 51.79.167.208 |
| ticket.ausecurity.best (osTicket helpdesk) | 51.79.166.209 |
| Admin login and dashboard (/api/auth/login, /dashboard) | 51.79.166.148 |

Network services discovered across the in-scope hosts: SSH (22), HTTP (80), HTTPS (443), and HTTP-alternate (8080).

## Methodology

* OWASP Web Security Testing Guide (WSTG) for web-application testing.
* Network service enumeration and banner/version discovery.
* Passive OSINT and enumeration, plus non-destructive active testing (port/version discovery and manual web-application testing of the FastAPI-style backend, WordPress, and osTicket).

No brute-force, denial-of-service, or destructive testing was performed.

## Limitations

* SSH (port 22) was open on all three hosts but was not brute-forced or exploited; only the version banner was recorded.
* No destructive or denial-of-service testing was performed.
* WordPress did not expose identifiable third-party plugins, so plugin-specific testing was not possible.
* Filesystem-level source review of osTicket was not possible without host access."""

with open(SRC, "r", encoding="utf-8") as f:
    proj = json.load(f)

for section in proj["sections"]:
    sid = section["id"]
    if sid == "executive_summary":
        section["data"]["executive_summary"] = executive_summary
        section["status"] = "finished"
    elif sid == "scope":
        section["data"]["scope"] = scope
        section["data"]["start_date"] = "2026-09-17"
        section["data"]["end_date"] = "2026-09-17"
        section["data"]["duration"] = "1 person day"
        section["data"]["provided_users"] = "No test accounts or credentials were provided. All testing was performed unauthenticated from an external position."
        section["status"] = "finished"
    elif sid == "customer":
        section["data"]["customer_name"] = "Ausecurity"
        section["data"]["customer_address"] = {
            "city": "Paddington, NSW 2021",
            "street": "63 Paddington St",
        }
        section["data"]["receiver_name"] = "Vinh Dinh"
        section["status"] = "finished"
    elif sid == "other":
        section["data"]["title"] = "Ausecurity Penetration Test Report"
        section["data"]["report_date"] = "2026-09-17"
        section["data"]["report_version"] = "1.1"
        section["data"]["list_of_changes"] = []
        section["data"]["draft"] = False
        section["status"] = "finished"
    elif sid == "appendix":
        section["data"]["appendix_sections"] = []
        section["status"] = "finished"

with open(DST, "w", encoding="utf-8") as f:
    json.dump(proj, f, indent=2, ensure_ascii=False)

print(f"Wrote {DST}")
print("Sections:")
for s in proj["sections"]:
    print(f"  - {s['id']}: {s['status']}")
