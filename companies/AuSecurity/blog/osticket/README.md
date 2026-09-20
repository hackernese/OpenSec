# Intentionally Vulnerable osTicket Docker Lab

This lab runs **osTicket 1.18.4** on Apache/PHP with MariaDB and deliberately includes:

- Apache directory listing (`Options +Indexes`).
- A web-accessible fake backup file at `/archives/backup.bak`.
- Fake credentials/tokens inside that backup file.
- Localhost-only port binding by default.

> **Training only.** Do not publish this container to the Internet or reuse this Apache configuration in production.

## Start

```bash
docker compose up -d --build
```

Then open:

- osTicket: `http://127.0.0.1:8080/`
- osTicket installer: `http://127.0.0.1:8080/setup/`
- Vulnerable directory listing: `http://127.0.0.1:8080/archives/`
- Exposed backup: `http://127.0.0.1:8080/archives/backup.bak`

## Complete the osTicket web installer

Use these database settings:

| Setting | Value |
|---|---|
| MySQL Hostname | `db` |
| MySQL Database | `osticket` |
| MySQL Username | `osticket` |
| MySQL Password | `osticket_lab_password` |

Choose whatever helpdesk/admin name, email, username and password you want for the lab.

After installation, osTicket normally recommends removing the setup directory and tightening `include/ost-config.php`. For a realistic lab you may do that while leaving the intentional `/archives/` exposure in place.

Example:

```bash
docker exec osticket-vulnerable-lab rm -rf /var/www/html/setup
docker exec osticket-vulnerable-lab chmod 0644 /var/www/html/include/ost-config.php
```

## Verify the intentional exposure

```bash
curl -i http://127.0.0.1:8080/archives/
curl http://127.0.0.1:8080/archives/backup.bak
```

The first request should return an Apache-generated directory index containing `backup.bak`; the second should print the fake secret material.

## Stop / reset

Stop containers:

```bash
docker compose down
```

Delete the database as well and return to a fresh installer state:

```bash
docker compose down -v
```

## Why this is intentionally vulnerable

Directory indexing itself can disclose filenames and forgotten artifacts. Combined with backup/config files placed below the web root, it can expose credentials, API tokens, source code, database dumps or internal configuration. This lab deliberately recreates that class of deployment mistake without using any real secret.
