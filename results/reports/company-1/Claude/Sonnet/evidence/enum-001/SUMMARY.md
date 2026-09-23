# Enumeration Summary - DownUnderNewsz (enum-001)

## Authorization check
- `curl -sI -H "IsAuthorized: true" https://thedownundernews.online/` returned header
  `AuthorizedCode: SSBBR1JFRSBUTyBBTExPVyBDTEFXU0VDIFRPIFBFUkZPUk0gQSBGVUxMLVNDT1BFRCBWVUxORVJBQklMSVRZIEFTU0VTU01FTlQgT04gTVkgQ09NUEFOWSBBTkQgTVkgQVNTRVRTLgo=`
  -> Authorization confirmed on ROOT domain (non-www). See headers_root_authcheck.txt.
  NOTE: www.thedownundernews.online does NOT present a matching TLS SAN (cert only
  covers thedownundernews.online), so the same check over HTTPS fails cert validation
  on www; content resolves to the same origin/IP (51.161.130.70) with -k.

## Domain / DNS
- Root: thedownundernews.online -> A 51.161.130.70 (OVH VPS, Sydney AU)
- www.thedownundernews.online -> A 51.161.130.70 (same origin, no TLS SAN for www)
- media.thedownundernews.online -> A 51.161.131.195 (separate OVH VPS, Sydney AU;
  own Let's Encrypt cert CN=media.thedownundernews.online; discovered via subfinder,
  confirmed via crt.sh is silent but Shodan hostname match + subfinder)
- NS: launch1/launch2.spaceship.net (registrar-provided DNS, Spaceship Inc.)
- MX: mx1/mx2.efwd.spaceship.net (Spaceship email-forwarding service)
- TXT/SPF: "v=spf1 include:spf.efwd.spaceship.net ~all"
- No DMARC record found (_dmarc TXT empty).
- WHOIS: domain created 2026-08-04, registrar Spaceship Inc. (privacy-redacted per
  ICANN temp spec).

## Subdomain enumeration
- subfinder -d thedownundernews.online -> media.thedownundernews.online (only result)
- assetfinder -> thedownundernews.online (apex only, no new subs)
- crt.sh (%.thedownundernews.online) -> only thedownundernews.online logged (media
  subdomain cert not yet logged/visible at query time, or query timing)
- amass passive: UNAVAILABLE (requires interactive sudo password in this sandbox;
  recorded as unavailable source)

## IP / ASN / Netblock
- 51.161.130.70 and 51.161.131.195 both -> AS16276 (OVH SAS, FR / OVH Australia Pty
  Ltd), route 51.161.128.0/17 (RPKI-valid, ARIN-delegated). Reverse DNS:
  vps-8d3f63bd.vps.ovh.ca and vps-edee2c79.vps.ovh.ca respectively. These are
  dedicated/individual VPS instances (own SSH/HTTPS, own TLS cert per host), not a
  shared multi-tenant CDN edge -> treated as dedicated hosting, not third-party CDN.
- Netblock 51.161.128.0/17 itself remains OVH-owned shared provider space (not
  exclusively the business's) -> classified as hosting infra context only, not an
  owned asset.

## Shodan
- shodan host 51.161.130.70: nginx, HTTP 200, title "The Down Under News – ...",
  OpenSSH 10.0p2 Debian 13.
- shodan host 51.161.131.195: nginx, HTTP 80->301, HTTPS 502 Bad Gateway (backend
  down/misconfigured), FTP port 21 open, OpenSSH 10.0p2 Debian 13.
- shodan search hostname:thedownundernews.online / media.thedownundernews.online
  returned only these two hosts - no additional attributed infrastructure found.

## Page-source review (homepage, authorized fetch)
- Referenced 3rd-party static assets only: cdn.jsdelivr.net, fonts.googleapis.com,
  fonts.gstatic.com (Google Fonts + jsDelivr CDN - third_party, not in scope).
- Footer explicitly states: 'Domain: thedownundernews.it.com' (self-declared alias
  domain by the target's own official site).
- No social-media links found in the fetched homepage HTML.
- No robots.txt or sitemap.xml present (404).

## thedownundernews.it.com investigation
- No A/AAAA/NS records via local resolver, 8.8.8.8, or 1.1.1.1.
- WHOIS (verisign .com registry, since it.com subdomains are 3rd-level names under
  the it.com reseller domain) returned "No match" for the queried string (expected,
  as it.com is a subdomain-reseller domain, not a standalone SLD).
- No crt.sh certificate history found for this name.
- curl to http/https timed out / no response - domain name is NOT currently live.
- Classified as "candidate" (self-declared by the org's own site, but unresolvable /
  unverifiable technically at this time - could be an aspirational/legacy/planned
  alias, or a copy-paste template remnant).

## Tools unavailable / limitations
- amass (active+passive combined engine) blocked by sandbox sudo prompt.
- Broad organization/aliases web search blocked by Google's JS-redirect page in the
  webfetch tool; no alternate search API configured.
- No SecurityTrails/VirusTotal/Censys API keys detected in environment; Shodan API
  key was available and used.
