import http.cookiejar, os, re, urllib.parse, urllib.request
out = "/home/research/Projects/Imagur/evidence/assess-auth-002"
cj = http.cookiejar.MozillaCookieJar(os.path.join(out, "cj"))
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
opener.addheaders = [("User-Agent", "ClawSec-Imagur-Assessment")]
data = urllib.parse.urlencode({
    "email": "clawsec.imagur.assess+2026b@gmail.com",
    "password": "ClawSecTest-9f3Kq",
}).encode()
req = urllib.request.Request("https://imagesharer.xyz/login", data=data, method="POST")
try:
    resp = opener.open(req, timeout=20)
except urllib.error.HTTPError as e:
    resp = e
print("login", resp.getcode(), resp.geturl())
dash = opener.open("https://imagesharer.xyz/dashboard", timeout=20).read().decode("utf-8", "replace")
open(os.path.join(out, "dashboard.html"), "w").write(dash)
print("dash_size", len(dash))
print("empty", "haven't uploaded" in dash)
print("img_count", len(re.findall(r"/images/[0-9a-f-]{36}", dash)))
prof = opener.open("https://imagesharer.xyz/profile", timeout=20).read().decode("utf-8", "replace")
open(os.path.join(out, "profile.html"), "w").write(prof)
m = re.search(r"Images uploaded</span>\s*<span>(\d+)</span>", prof, re.S)
print("images_uploaded", m.group(1) if m else "unknown")
cj.save(ignore_discard=True, ignore_expires=True)
