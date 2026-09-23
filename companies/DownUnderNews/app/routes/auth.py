"""
Authentication routes – login, logout, password change, profile.
These serve both the JSON API and redirect-based admin panel flows.
"""
import secrets
from datetime import datetime, timezone

from flask import Blueprint, request, jsonify, redirect, url_for, render_template, make_response
from flask_jwt_extended import (
    create_access_token,
    get_jwt_identity,
    set_access_cookies,
    unset_jwt_cookies,
    jwt_required,
)
from app import db, bcrypt
from app.models import User
from app.utils import get_current_user, error, success

auth_bp = Blueprint("auth", __name__)


# --------------------------------------------------------------------------- #
# Login
# --------------------------------------------------------------------------- #
@auth_bp.route("", methods=["GET"])
def login_page():
    return render_template("admin/login.html")


@auth_bp.route("/login", methods=["POST"])
def login():
    """Accept JSON or form-encoded credentials, return JWT in cookie."""
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form.to_dict()

    identifier = data.get("username") or data.get("email", "")
    password = data.get("password", "")

    if not identifier or not password:
        if request.is_json:
            return error("Username/email and password are required", 400)
        return render_template("admin/login.html", error="Username and password are required"), 400

    # Find user by username OR email
    user = User.query.filter(
        (User.username == identifier) | (User.email == identifier)
    ).first()

    if not user or not bcrypt.check_password_hash(user.password_hash, password):
        if request.is_json:
            return error("Invalid credentials", 401)
        return render_template("admin/login.html", error="Invalid username or password"), 401

    if not user.is_active:
        if request.is_json:
            return error("Account is deactivated", 403)
        return render_template("admin/login.html", error="Your account has been deactivated"), 403

    token = create_access_token(identity=str(user.id))

    if request.is_json:
        return jsonify({"token": token, "user": user.to_dict()}), 200

    # Browser flow – set cookie and redirect
    resp = make_response(redirect(url_for("admin.dashboard")))
    set_access_cookies(resp, token)
    return resp


# --------------------------------------------------------------------------- #
# Logout
# --------------------------------------------------------------------------- #
@auth_bp.route("/logout", methods=["GET", "POST"])
def logout():
    resp = make_response(redirect(url_for("auth.login_page")))
    unset_jwt_cookies(resp)
    return resp


# --------------------------------------------------------------------------- #
# Profile (JSON API)
# --------------------------------------------------------------------------- #
@auth_bp.route("/profile", methods=["GET"])
@jwt_required(locations=["headers", "cookies"])
def profile():
    user = get_current_user()
    if not user:
        return error("User not found", 404)
    return jsonify({"user": user.to_dict()})


@auth_bp.route("/profile", methods=["PUT"])
@jwt_required(locations=["headers", "cookies"])
def update_profile():
    user = get_current_user()
    if not user:
        return error("User not found", 404)

    data = request.get_json() or {}
    if "first_name" in data:
        user.first_name = data["first_name"].strip()[:100]
    if "last_name" in data:
        user.last_name = data["last_name"].strip()[:100]
    if "email" in data:
        email = data["email"].strip().lower()
        existing = User.query.filter(User.email == email, User.id != user.id).first()
        if existing:
            return error("Email already in use", 409)
        user.email = email

    user.updated_at = datetime.now(timezone.utc)
    db.session.commit()
    return jsonify({"user": user.to_dict()})


@auth_bp.route("/change-password", methods=["POST"])
@jwt_required(locations=["headers", "cookies"])
def change_password():
    user = get_current_user()
    if not user:
        return error("User not found", 404)

    data = request.get_json() or {}
    current_password = data.get("current_password", "")
    new_password = data.get("new_password", "")

    if not bcrypt.check_password_hash(user.password_hash, current_password):
        return error("Current password is incorrect", 401)

    if len(new_password) < 8:
        return error("New password must be at least 8 characters", 400)

    user.password_hash = bcrypt.generate_password_hash(new_password).decode("utf-8")
    user.updated_at = datetime.now(timezone.utc)
    db.session.commit()
    return success(message="Password updated successfully")
