#!/usr/bin/env python3
"""Build corrected findings.json using the backtick-formatted text from the
previous (rendering-clean) project export, applying the two CVSS/severity
corrections and ordering to match findings.txt."""
import json

BASE = "/home/research/Projects/DownUnderNewsz"

ORDER = [
    "Stored Cross-Site Scripting (XSS) via Article Content",
    "Malicious File Upload — HTML Served as text/html (Stored XSS)",
    "Anonymous FTP Read Access to Media Server",
    "Missing Cross-Site Request Forgery (CSRF) Protection",
    "Session Cookie Missing Secure and SameSite Flags",
    "Sensitive Information Disclosure via Unauthenticated API",
    "Weak and Shared Administrator/User Credentials",
    "TLS Certificate Hostname Mismatch on www Subdomain",
    "Missing Security Headers",
]

old = json.load(open(f"{BASE}/old.json", encoding="utf-8"))
by_title = {f["data"]["title"]: f["data"] for f in old["findings"]}

# Corrections per updated findings.txt (severity labels authoritative)
# 1) Sensitive Information Disclosure: Low -> Medium
d = by_title["Sensitive Information Disclosure via Unauthenticated API"]
d["summary"] = d["summary"].replace("**Severity:** Low", "**Severity:** Medium", 1)

# 2) Weak and Shared Credentials: CVSS removed -> n/a (severity stays Low)
by_title["Weak and Shared Administrator/User Credentials"]["cvss"] = "n/a"

out = []
for title in ORDER:
    data = by_title[title]
    out.append({"status": "finished", "data": data})

with open(f"{BASE}/findings.json", "w", encoding="utf-8") as fp:
    json.dump(out, fp, indent=2, ensure_ascii=False)

print(f"Wrote {len(out)} findings to findings.json")
for i, f in enumerate(out, 1):
    d = f["data"]
    sev = d["summary"].split("\n")[0]
    print(f"  {i}. [{d['cvss']}] {sev} | {d['title']}")
