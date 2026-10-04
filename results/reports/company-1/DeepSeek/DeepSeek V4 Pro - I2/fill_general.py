#!/usr/bin/env python3
import json

with open("/home/research/Projects/DownUnderNewsz/general.json", "r") as f:
    proj = json.load(f)

executive_summary = """This report documents an authorized full-scope vulnerability assessment of **DownUnderNewsz**, a small independent online news outlet. The company operates a Flask-based news website with a role-based administration panel (administrator, writer, and editor roles) hosted on a virtual private server, together with a separate server used to store and serve media files.

The assessment was conducted between 17 and 18 September 2026 and covered the company's primary news website (`thedownundernews.online`) and its media host (`media.thedownundernews.online`). Five issues were confirmed in total: **one high-severity, two medium-severity, and two low-severity** findings.

**Key takeaways for leadership**

The most important issue is a stored cross-site scripting (XSS) vulnerability. A staff member who can publish articles (the "editor" role) could place malicious code inside an article that would then run automatically in the browser of anyone who visits the site, including other logged-in staff. This could allow an attacker to perform actions on behalf of visitors and undermine the security of the whole application. Reassuringly, the separation between staff roles, the permission to publish, and the checks on uploaded file types were all found to be working correctly.

Two medium-severity issues relate to configuration: the media server currently allows anyone on the internet to read its stored files without logging in, and the administration panel lacks protection against a type of attack known as cross-site request forgery (CSRF).

The two low-severity items concern missing security settings on website cookies and missing security headers on the web servers.

**Recommended priorities**

1. Sanitise article content on the server so that scripts cannot be stored inside articles.
2. Disable anonymous (unauthenticated) access to the media server's FTP service.
3. Add CSRF protection to the administration panel.
4. Apply the missing cookie flags and security headers.

Overall, the application has a sound foundation, and every issue identified can be resolved with targeted configuration and code changes. Addressing the high-severity item first will materially reduce risk to the business and its readers."""

scope = """The following in-scope systems were assessed during this engagement:

| System | Address | Description |
|:---|:---|:---|
| thedownundernews.online / www.thedownundernews.online | 51.161.130.70 | Primary news web application (Flask, nginx); ports 22 (SSH) and 443 (HTTPS) |
| media.thedownundernews.online | 51.161.131.195 | Dedicated media VPS (vsftpd 3.0.5 on 21, OpenSSH 10.0p2 on 22, nginx on 80/443) |

Third-party infrastructure (OVH AS16276, Spaceship registrar/DNS/email, Google Fonts, jsDelivr, Let's Encrypt) was explicitly **out of scope**."""

provided_users = """The following owner-provided test accounts were used for authenticated testing:

* admin
* writer
* editor
"""

for section in proj["sections"]:
    if section["id"] == "executive_summary":
        section["data"]["executive_summary"] = executive_summary
    elif section["id"] == "scope":
        section["data"]["scope"] = scope
        section["data"]["start_date"] = "2026-09-17"
        section["data"]["end_date"] = "2026-09-18"
        section["data"]["duration"] = "2 days"
        section["data"]["provided_users"] = provided_users
    elif section["id"] == "customer":
        section["data"]["customer_name"] = "DownUnderNewsz"
        section["data"]["customer_address"] = {
            "city": "Fairfield VIC 3078, Australia",
            "street": "22 Arthur St",
        }
        section["data"]["receiver_name"] = "Vinh Dinh"
    elif section["id"] == "other":
        section["data"]["title"] = "DownUnderNewsz - Penetration Test Report"
        section["data"]["report_date"] = "2026-09-18"
        section["data"]["report_version"] = "1.0"
        section["data"]["list_of_changes"] = [
            {
                "date": "2026-09-18",
                "description": "Initial release",
                "version": "1.0",
            }
        ]
        section["data"]["draft"] = False
    elif section["id"] == "appendix":
        section["data"]["appendix_sections"] = [
            {
                "title": "Assessment Methodology",
                "content": (
                    "The assessment combined passive and enumeration reconnaissance "
                    "(DNS, WHOIS/RDAP, certificate transparency, and Shodan), authenticated "
                    "web-application testing using owner-provided test accounts (admin, writer, "
                    "editor), targeted service/version scanning on known-open ports only, and "
                    "manual verification of all findings."
                ),
            },
            {
                "title": "Coverage and Limitations",
                "content": (
                    "Coverage included authentication and session management, role-based access "
                    "control and IDOR, SQL injection, cross-site scripting (reflected and stored), "
                    "CSRF, file-upload validation, FTP/HTTP on the media host, and HTTP security "
                    "headers.\n\n"
                    "The following limitations apply: no destructive testing and no brute-force or "
                    "password-spraying were performed per engagement rules (the JWT signing secret "
                    "strength was not brute-forced); the media host HTTPS backend returned 502 "
                    "(upstream down) during the assessment; SQL injection was tested but not "
                    "exhaustively; and WHOIS registrant data is privacy-redacted."
                ),
            },
            {
                "title": "Severity Rating Scale",
                "content": (
                    "Findings are rated using the CVSS v3.1 severity bands:\n\n"
                    "| Rating | CVSS v3.1 Score |\n"
                    "|:---|:---|\n"
                    "| Critical | 9.0 - 10.0 |\n"
                    "| High | 7.0 - 8.9 |\n"
                    "| Medium | 4.0 - 6.9 |\n"
                    "| Low | 0.1 - 3.9 |\n"
                    "| Informational / None | 0.0 |"
                ),
            },
        ]
    # Mark every section as finished for a clean, final report
    section["status"] = "finished"

with open("/home/research/Projects/DownUnderNewsz/general_filled.json", "w") as f:
    json.dump(proj, f, indent=2)

print("Wrote general_filled.json")
print("title:", next(s["data"]["title"] for s in proj["sections"] if s["id"] == "other"))
print("draft:", next(s["data"]["draft"] for s in proj["sections"] if s["id"] == "other"))
