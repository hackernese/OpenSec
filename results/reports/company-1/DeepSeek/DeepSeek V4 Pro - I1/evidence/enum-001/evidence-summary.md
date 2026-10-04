# Enumeration Evidence — DownUnderNewsz (enum-001)

Date (UTC): 2026-09-17
Analyst: enumeration sub-agent (ClawSec)

## Scope seeds (from orchestrator)
- canonical name: DownUnderNewsz
- website: https://www.thedownundernews.online/ (apex https://thedownundernews.online/)
- owner: Vinh Dinh
- address: 22 Arthur St, Fairfield VIC 3078, Australia
- supplied IP (TLS obs): 51.161.130.70

## DNS observations (dig) — thedownundernews.online
- A: 51.161.130.70
- AAAA: (none)
- NS: launch1.spaceship.net, launch2.spaceship.net  (Spaceship Inc, registrar/DNS)
- MX: mx1.efwd.spaceship.net, mx2.efwd.spaceship.net  (Spaceship email forwarding)
- TXT/SPF: "v=spf1 include:spf.efwd.spaceship.net ~all"
- SOA: launch1.spaceship.net. support.spaceship.com. serial 1788622483
- DNSSEC DS present (signedDelegation), algorithm 13
- CAA: (none)
- DMARC (_dmarc): (none)
- DKIM (default, google, smtp, mail, k1, k2, selector1/2): (none)
- No wildcard DNS (random labels NXDOMAIN)

## Subdomains discovered
- www.thedownundernews.online -> 51.161.130.70 (A)
- media.thedownundernews.online -> 51.161.131.195 (A)  [subfinder + dig confirmed]
- members.thedownundernews.online: FALSE POSITIVE (resolver timeout artifact; NXDOMAIN on recheck)

## IP / hosting observations
- 51.161.130.70
  - PTR: vps-8d3f63bd.vps.ovh.ca
  - Shodan: City Sydney, AU; Org "OVH Australia PTY LTD"; open ports 22 (OpenSSH 10.0p2 Debian), 443 (nginx)
  - HTTP title: "The Down Under News – Australia's Independent Online Newspaper"
  - TLS: Let's Encrypt, CN=thedownundernews.online, SAN DNS:thedownundernews.online (only)
- 51.161.131.195
  - PTR: vps-edee2c79.vps.ovh.ca
  - Shodan: City Sydney, AU; Org OVH Australia PTY LTD; open ports 21 (ftp), 22 (ssh), 80 (nginx), 443 (nginx)
  - 443 -> 502 Bad Gateway; cert CN=media.thedownundernews.online
- Both IPs within 51.161.130.0/23 (VPS-SYD2 per ARIN RDAP)
- ASN (Team Cymru): AS16276 | OVH - OVH SAS, FR; netblock 51.161.128.0/17
- RDAP ARIN: net 51.161.130.0/23, entity NOC11876-ARIN, OVH, Montreal QC Canada

## Domain registration
- Registrar: Spaceship, Inc. (IANA 3862)
- Registry expiry: 2027-08-04; updated 2026-08-09
- No registrant data (privacy)

## Web content observations (light active, GET only)
- nginx; HTTP->HTTPS 301 redirect on apex
- /static/js/main.js reveals client calls API at /api/articles?limit=5
- /api/articles returns JSON; author email admin@thedownundernews.it.com
- Contact page emails: advertising@, editorial@, corrections@ ... @thedownundernews.it.com
- Footer link: https://thedownundernews.it.com
- Social icons present (facebook/instagram/twitter/youtube) — no concrete URLs extracted
- Third-party references: cdn.jsdelivr.net, fonts.googleapis.com, fonts.gstatic.com

## thedownundernews.it.com investigation
- dig: NXDOMAIN (no A/NS/MX/TXT/SOA)
- whois -h whois.centralnic.com: "DOMAIN NOT FOUND" (not registered under .it.com registry)
- Conclusion: referenced domain, currently UNREGISTERED (potential dangling reference)

## Certificate transparency (crt.sh)
- Only certs for thedownundernews.online (Let's Encrypt, 2026-09-05)
- No additional subdomains; no certs found by IP query
- Keyword "downunder" search: only unrelated third-party orgs (horsemanship, geosolutions, etc.)

## Tools used
dig, host, whois, curl, openssl, subfinder, amass (passive; no results), shodan host/search,
crt.sh API, Team Cymru ASN DNS, ARIN RDAP.

## Unavailable / limits
- amass passive returned no results (timed out / no data)
- No SecurityTrails / VirusTotal / Censys API keys checked for historical DNS
- media.thedownundernews.online backend is 502 (not explored further)
