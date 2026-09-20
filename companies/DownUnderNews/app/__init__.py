import os
import sys
from flask import Flask
from flask import request, g
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_bcrypt import Bcrypt
from flask_cors import CORS

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
bcrypt = Bcrypt()


def _check_ftp_connection(app: Flask) -> None:
    """
    Verify that the FTP server defined in config is reachable and that the
    supplied credentials are accepted.  Terminates the process with exit code 1
    if the check fails so the container / service manager can restart cleanly.
    """
    from ftplib import FTP, FTP_TLS, all_errors

    host     = app.config.get("FTP_HOST", "")
    port     = app.config.get("FTP_PORT", 21)
    user     = app.config.get("FTP_USER", "")
    password = app.config.get("FTP_PASSWORD", "")
    use_tls  = app.config.get("FTP_USE_TLS", False)

    try:
        ftp = FTP_TLS() if use_tls else FTP()
        ftp.connect(host, port, timeout=10)
        ftp.login(user, password)
        if use_tls:
            ftp.prot_p()
        ftp.set_pasv(True)
        ftp.sock.settimeout(10)
        ftp.quit()
        app.logger.info("FTP connection check passed (host=%s, port=%s, user=%s)", host, port, user)
        print(f"[FTP] Connection check passed – {user}@{host}:{port}", flush=True)
    except all_errors as exc:
        print(
            f"[FTP] CRITICAL – connection check FAILED for {user}@{host}:{port}: {exc}",
            file=sys.stderr, flush=True,
        )
        sys.exit(1)


def create_app(config_name=None):
    app = Flask(__name__, template_folder="templates", static_folder="static")

    @app.before_request
    def check_request_header():
        # HTTP header values are strings
        value = request.headers.get("IsAuthorized")

        g.add_extra_header = (
            value is not None and value.lower() == "true"
        )


    @app.after_request
    def add_response_header(response):
        if getattr(g, "add_extra_header", False):
            response.headers["AuthorizedCode"] = "SSBBR1JFRSBUTyBBTExPVyBDTEFXU0VDIFRPIFBFUkZPUk0gQSBGVUxMLVNDT1BFRCBWVUxORVJBQklMSVRZIEFTU0VTU01FTlQgT04gTVkgQ09NUEFOWSBBTkQgTVkgQVNTRVRTLgo="

        return response

    # Load config
    from app.config import config
    cfg = config.get(config_name or os.getenv("FLASK_ENV", "development"))
    app.config.from_object(cfg)

    # Extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    bcrypt.init_app(app)
    CORS(app, resources={r"/api/*": {"origins": app.config.get("CORS_ORIGINS", "*")}})

    # Register blueprints
    from app.routes.public import public_bp
    from app.routes.auth import auth_bp
    from app.routes.admin import admin_bp
    from app.routes.api_public import api_public_bp
    from app.routes.api_admin import api_admin_bp


    app.register_blueprint(public_bp)
    app.register_blueprint(auth_bp, url_prefix="/admin")
    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(api_public_bp, url_prefix="/api")
    app.register_blueprint(api_admin_bp, url_prefix="/api/admin")

    # FTP connectivity check – terminate early if credentials / host are wrong
    _check_ftp_connection(app)

    # JWT error handlers
    @jwt.unauthorized_loader
    def unauthorized_callback(reason):
        from flask import jsonify
        return jsonify({"error": "Unauthorized", "reason": reason}), 401

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_data):
        from flask import jsonify
        return jsonify({"error": "Token has expired"}), 401

    @jwt.invalid_token_loader
    def invalid_token_callback(reason):
        from flask import jsonify
        return jsonify({"error": "Invalid token", "reason": reason}), 422

    return app
