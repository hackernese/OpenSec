import urllib.request, urllib.parse, http.cookiejar, os, re
base = "https://imagesharer.xyz"
out = "/home/research/Projects/Imagur/evidence/assess-auth-002"
os.makedirs(out, exist_ok=True)
cj = http.cookiejar.MozillaCookieJar(os.path.join(out, "cj"))
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
opener.addheaders = [("User-Agent", "ClawSec-Imagur-Assessment")]
data = urllib.parse.urlencode({
    "email": "clawsec.imagur.assess+2026b@gmail.com",
    "password": "ClawSecTest-9f3Kq",
    "confirm": "ClawSecTest-9f3Kq",
}).encode()
req = urllib.request.Request(base + "/register", data=data, method="POST")
try:
    resp = opener.open(req, timeout=20)
except urllib.error.HTTPError as e:
    resp = e
print("reg", resp.getcode(), resp.geturl())
body = opener.open(base + "/images/upload", timeout=20).read().decode("utf-8", "replace")
open(os.path.join(out, "upload.html"), "w").write(body)
m = re.search(r'name="user_id" value="([^"]+)"', body)
print("user_id", m.group(1) if m else "missing")
print("size", len(body))
cj.save(ignore_discard=True, ignore_expires=True)
