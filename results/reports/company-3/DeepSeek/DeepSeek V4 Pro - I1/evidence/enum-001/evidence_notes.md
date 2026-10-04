# Enumeration Evidence Notes — enum-001

Target: Imagur (FShare / ImageSharer), imagesharer.xyz

## DNS
- A record: imagesharer.xyz -> 51.161.131.44
- AAAA: none
- NS: launch1.spaceship.net, launch2.spaceship.net (Spaceship DNS)
- MX: none
- TXT: none
- CAA: none
- SOA: launch1.spaceship.net. support.spaceship.com. (serial 1789376610)
- DNSSEC: signedDelegation (DS keyTag 61483, alg 13)
- Reverse DNS 51.161.131.44: vps-ad2c3eab.vps.ovh.ca

## Subdomains (via dnsx brute force + HTML source)
- www.imagesharer.xyz -> 51.161.131.44
- resources.imagesharer.xyz -> CNAME d273uevi0662l0.cloudfront.net (CloudFront)

## Domain registration (RDAP/WHOIS)
- Registrar: Spaceship, Inc. (IANA 3862)
- Created: 2026-09-06, Expires: 2027-09-06
- Status: serverTransferProhibited, clientTransferProhibited
- Registrant not disclosed (privacy)

## IP / Hosting
- 51.161.131.44 in netblock VPS-SYD2 (51.161.130.0 - 51.161.131.255), parent 51.161.128.0/17
- ASN: AS16276 (OVH), OVH Australia PTY LTD, Sydney
- Shodan: only port 80 observed (2026-09-10), "Welcome to nginx!" title

## HTTP observations (direct, low-impact)
- https://imagesharer.xyz/ -> 302 -> /dashboard -> /login (200). Title "Log in — Imager"
- Server: nginx, X-Powered-By: PHP/8.2.33, X-Frame-Options DENY, etc.
- http://imagesharer.xyz/ -> 301 to https
- https://www.imagesharer.xyz/ -> same app (title "Log in — Imager")
- http://51.161.131.44:8080/ -> 302 -> /dashboard -> /login. Server: Apache/2.4.68 (Debian), PHP 8.2.33. Same "Imager" app.
- Ports 80, 443, 8080 open (HTTP); 8000/8443/8880/3000 closed.

## TLS certificate
- CN=imagesharer.xyz, SAN: DNS:imagesharer.xyz only
- Issuer: Let's Encrypt (CN=YE2), valid 2026-09-14 -> 2026-12-13
- No CT log entries on crt.sh (not yet indexed)

## AWS / cloud assets
- CloudFront distribution: d273uevi0662l0.cloudfront.net (origin: Amazon S3). Server: AmazonS3, "Error from cloudfront".
  - Note: accessing via resources.imagesharer.xyz fails TLS because CloudFront cert SAN is only *.cloudfront.net
- S3 bucket existence check:
  - imagesharer.s3.amazonaws.com -> 403 AccessDenied (x-amz-bucket-region: ap-northeast-1)  [exists]
  - fshare.s3.amazonaws.com -> 403 AccessDenied (x-amz-bucket-region: eu-west-1)  [exists]
  - imagur.s3.amazonaws.com -> 404 [does not exist]
  - imagesharer-resources.s3.amazonaws.com -> 404
  - resources-imagesharer.s3.amazonaws.com -> 404

## SECURITY OBSERVATION (finding, not used)
- /js/awsvalid.js (client-side) contains a hardcoded AWS access key ID, secret
  access key, and region "ap-southeast-2" (Sydney) in a source comment.
  - File saved at evidence/enum-001/awsvalid.js
  - Credentials were NOT used for authentication/enumeration (out of scope for enumeration phase).
  - Indicates the business uses AWS (ap-southeast-2 = Sydney region).

## Third-party references in page HTML
- https://encrypted-tbn0.gstatic.com (Google avatar image)
- https://resources.imagesharer.xyz (own CDN hostname)

## Rejected (neighbor co-tenants on OVH /24 — NOT in scope)
Shodan net:51.161.131.0/24 shows many unrelated OVH VPS customers:
actualisedesign.com, vapexpro.fr, ecitizenproject.com, nanonator.com (mail),
aussiewave.au (ns2), plus many vps-*.vps.ovh.ca hosts. None tied to Imagur/ImageSharer/FShare.
