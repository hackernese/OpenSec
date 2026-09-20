import os
from datetime import timedelta


class BaseConfig:
    SECRET_KEY = os.getenv("SECRET_KEY", "change-me-in-production")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "change-me-jwt-secret")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=int(os.getenv("JWT_EXPIRES_HOURS", "8")))
    JWT_TOKEN_LOCATION = ["headers", "cookies"]
    JWT_COOKIE_SECURE = False
    JWT_COOKIE_CSRF_PROTECT = False
    JWT_ACCESS_COOKIE_PATH = "/"
    JWT_REFRESH_COOKIE_PATH = "/api/admin/refresh"

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = (
        f"postgresql://{os.getenv('DB_USER', 'news_user')}:"
        f"{os.getenv('DB_PASSWORD', 'news_pass')}@"
        f"{os.getenv('DB_HOST', 'localhost')}:"
        f"{os.getenv('DB_PORT', '5432')}/"
        f"{os.getenv('DB_NAME', 'newspaper_db')}"
    )

    APP_URL = os.getenv("APP_URL", "http://localhost:5000")
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*")

    # FTP media server
    FTP_HOST       = os.getenv("FTP_HOST", "")
    FTP_PORT       = int(os.getenv("FTP_PORT", "21"))
    FTP_USER       = os.getenv("FTP_USER", "")
    FTP_PASSWORD   = os.getenv("FTP_PASSWORD", "")
    FTP_USE_TLS    = os.getenv("FTP_USE_TLS", "false").lower() == "true"
    FTP_UPLOAD_DIR = os.getenv("FTP_UPLOAD_DIR", "/uploads")   # remote path on FTP server
    MEDIA_BASE_URL = os.getenv("MEDIA_BASE_URL", "")           # public HTTP URL for stored files

    # Email (password reset)
    SMTP_HOST = os.getenv("SMTP_HOST", "localhost")
    SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USER = os.getenv("SMTP_USER", "")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
    MAIL_DEFAULT_SENDER = os.getenv("MAIL_FROM", "noreply@thedownundernews.it.com")

    # Upload limits
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50 MB


class DevelopmentConfig(BaseConfig):
    DEBUG = True
    JWT_COOKIE_SECURE = False


class ProductionConfig(BaseConfig):
    DEBUG = False
    JWT_COOKIE_SECURE = True
    JWT_COOKIE_CSRF_PROTECT = False


config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
