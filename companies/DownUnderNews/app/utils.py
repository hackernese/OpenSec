import re
import os
import uuid
import mimetypes
from ftplib import FTP, FTP_TLS, error_perm
from functools import wraps
from datetime import datetime, timezone
from flask import current_app, jsonify
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
from app.models import User


# --------------------------------------------------------------------------- #
# Slug helpers
# --------------------------------------------------------------------------- #

def slugify(text: str) -> str:
    """Convert text to a URL-friendly slug."""
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_-]+", "-", text)
    text = re.sub(r"^-+|-+$", "", text)
    return text


def unique_slug(base_slug: str, model, existing_id=None) -> str:
    """Return a slug that doesn't already exist in model.slug."""
    slug = base_slug
    counter = 1
    while True:
        query = model.query.filter_by(slug=slug)
        if existing_id:
            query = query.filter(model.id != existing_id)
        if not query.first():
            return slug
        slug = f"{base_slug}-{counter}"
        counter += 1


# --------------------------------------------------------------------------- #
# Pagination
# --------------------------------------------------------------------------- #

def paginate_query(query, page: int, per_page: int):
    """Return (items, total, pages) for a query."""
    total = query.count()
    items = query.offset((page - 1) * per_page).limit(per_page).all()
    pages = (total + per_page - 1) // per_page if per_page else 1
    return items, total, pages


# --------------------------------------------------------------------------- #
# Auth decorators
# --------------------------------------------------------------------------- #

def jwt_required_with_role(*roles):
    """Decorator: require JWT + optional role check."""
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request(locations=["headers", "cookies"])
            identity = get_jwt_identity()
            user = User.query.get(int(identity))
            if not user or not user.is_active:
                return jsonify({"error": "User not found or inactive"}), 401
            if roles and user.role not in roles:
                return jsonify({"error": "Insufficient permissions"}), 403
            return fn(*args, **kwargs)
        return wrapper
    return decorator


def get_current_user():
    identity = get_jwt_identity()
    return User.query.get(int(identity))


# --------------------------------------------------------------------------- #
# Media server helpers
# --------------------------------------------------------------------------- #

ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/gif", "image/webp"}
ALLOWED_DOC_TYPES = {"application/pdf", "application/msword",
                     "application/vnd.openxmlformats-officedocument.wordprocessingml.document"}
MAX_IMAGE_SIZE = 10 * 1024 * 1024   # 10 MB
MAX_DOC_SIZE = 50 * 1024 * 1024     # 50 MB


def _ftp_log(msg: str) -> None:
    """Print a timestamped FTP diagnostic line to stdout (always visible in docker compose logs)."""
    import datetime
    ts = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
    print(f"[FTP {ts}] {msg}", flush=True)


def _ftp_connect() -> FTP:
    """Open and return an authenticated FTP (or FTPS) connection.

    Passive mode is explicitly enabled so that the FTP server opens the data
    channel rather than trying to connect back to this container (active mode
    would be blocked by Docker NAT).  The same 30-second timeout is applied to
    both the control socket (via connect()) and the underlying socket so that
    data-channel operations (STOR, RETR, LIST) also time out instead of hanging
    indefinitely.
    """
    host     = current_app.config["FTP_HOST"]
    port     = current_app.config["FTP_PORT"]
    user     = current_app.config["FTP_USER"]
    password = current_app.config["FTP_PASSWORD"]
    use_tls  = current_app.config["FTP_USE_TLS"]

    _ftp_log(f"Connecting to {host}:{port} (TLS={use_tls}) ...")
    ftp = FTP_TLS() if use_tls else FTP()
    ftp.connect(host, port, timeout=30)
    _ftp_log(f"Control channel open – server banner: {ftp.getwelcome()!r}")

    _ftp_log(f"Logging in as '{user}' ...")
    ftp.login(user, password)
    _ftp_log("Login accepted.")

    if use_tls:
        ftp.prot_p()   # switch to encrypted data channel
        _ftp_log("TLS data channel (PROT P) negotiated.")

    # Force passive mode – the server opens the data port, not us.
    # This is the only mode that works reliably from inside a Docker container
    # because Docker NAT prevents the server from reaching us (active mode).
    ftp.set_pasv(True)
    _ftp_log("Passive mode enabled.")

    # Apply a socket-level timeout to the control connection so that any
    # subsequent data-channel command (STOR, LIST, etc.) also times out
    # instead of blocking forever if the data channel stalls.
    ftp.sock.settimeout(30)
    return ftp


def upload_to_media_server(file_stream, filename: str, content_type: str) -> dict:
    """
    Upload a file to the FTP media server.
    Returns dict with keys: url, filename, original_name, size
    """
    import io

    ext         = os.path.splitext(filename)[1]
    unique_name = f"{uuid.uuid4().hex}{ext}"
    remote_dir  = current_app.config["FTP_UPLOAD_DIR"].rstrip("/")
    base_url    = current_app.config["MEDIA_BASE_URL"].rstrip("/")

    # Read into memory to get size (ftplib needs a seekable stream for STOR)
    data = file_stream.read()
    size = len(data)

    _ftp_log(f"Starting upload: original='{filename}' stored_as='{unique_name}' size={size}B remote_dir='{remote_dir}'")

    ftp = _ftp_connect()

    _ftp_log("HERE ALREADY")

    try:
        # Make sure the remote directory exists
        _ftp_log(f"Changing to remote directory '{remote_dir}' ...")
        try:
            ftp.cwd(remote_dir)
            _ftp_log(f"CWD succeeded: now in '{remote_dir}'.")
        except error_perm:
            _ftp_log(f"'{remote_dir}' does not exist – creating recursively ...")
            parts = remote_dir.lstrip("/").split("/")
            path  = ""
            for part in parts:
                path += f"/{part}"
                try:
                    ftp.cwd(path)
                    _ftp_log(f"  CWD '{path}' OK.")
                except error_perm:
                    ftp.mkd(path)
                    ftp.cwd(path)
                    _ftp_log(f"  Created and entered '{path}'.")

        _ftp_log(f"Sending STOR {unique_name} ({size}B) – waiting for data channel ...")
        ftp.storbinary(f"STOR {unique_name}", io.BytesIO(data))
        _ftp_log(f"STOR complete – '{unique_name}' uploaded successfully.")
    finally:
        try:
            ftp.quit()
            _ftp_log("FTP connection closed (QUIT).")
        except Exception as e:
            _ftp_log(f"QUIT failed ({e}), forcing close.")
            ftp.close()

    _ftp_log(f"Upload done. Public URL: {base_url}/{unique_name}")
    return {
        "url":           f"{base_url}/{unique_name}",
        "filename":      unique_name,
        "original_name": filename,
        "size":          size,
    }


def delete_from_media_server(filename: str) -> bool:
    """Delete a file from the FTP media server. Returns True on success."""
    remote_dir = current_app.config["FTP_UPLOAD_DIR"].rstrip("/")

    ftp = _ftp_connect()
    try:
        ftp.cwd(remote_dir)
        ftp.delete(filename)
        return True
    except error_perm:
        # File not found or permission denied – treat as non-fatal
        return False
    finally:
        try:
            ftp.quit()
        except Exception:
            ftp.close()


def validate_file_upload(file):
    """
    Validate uploaded file. Returns (is_valid, error_message, media_type).
    """
    content_type = file.content_type or mimetypes.guess_type(file.filename)[0] or ""
    file.stream.seek(0, 2)
    size = file.stream.tell()
    file.stream.seek(0)

    if content_type in ALLOWED_IMAGE_TYPES:
        if size > MAX_IMAGE_SIZE:
            return False, f"Image exceeds 10MB limit ({size // 1024 // 1024}MB)", None
        return True, None, "image"
    elif content_type in ALLOWED_DOC_TYPES:
        if size > MAX_DOC_SIZE:
            return False, f"Document exceeds 50MB limit", None
        media_type = "pdf" if "pdf" in content_type else "document"
        return True, None, media_type
    else:
        return False, f"File type '{content_type}' is not allowed", None


# --------------------------------------------------------------------------- #
# Response helpers
# --------------------------------------------------------------------------- #

def success(data=None, message=None, status=200):
    resp = {"success": True}
    if message:
        resp["message"] = message
    if data is not None:
        resp.update(data)
    return jsonify(resp), status


def error(message, status=400, details=None):
    resp = {"error": message}
    if details:
        resp["details"] = details
    return jsonify(resp), status
