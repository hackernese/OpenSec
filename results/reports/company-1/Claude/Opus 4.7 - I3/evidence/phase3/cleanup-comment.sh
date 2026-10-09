#!/usr/bin/env bash
TARGET="https://www.thedownundernews.online"
JAR_A=/home/research/Projects/DownUnderNewsz/evidence/phase2/jar_admin.txt
EV=/home/research/Projects/DownUnderNewsz/evidence/phase3

echo "=== list all comments via admin ==="
curl -sS -k -b "$JAR_A" -o "$EV/comments-list.html" -w "status=%{http_code} size=%{size_download}\n" -m 15 "$TARGET/admin/comments"
grep -nE 'ClawSec|comment-id|data-id|/comments/[0-9]+|<tr|<td' "$EV/comments-list.html" | head -n 40

echo
echo "=== probe JSON api for comments ==="
for p in /api/admin/comments /api/comments; do
  printf '%s -> ' "$p"
  curl -sS -k -b "$JAR_A" -w "status=%{http_code} size=%{size_download}\n" -o /tmp/co.$$ -m 10 "$TARGET$p"
  head -c 500 /tmp/co.$$
  echo
done
rm -f /tmp/co.$$
