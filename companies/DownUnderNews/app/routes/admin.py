"""
Admin panel HTML page routes (protected by JWT cookie).
"""
from functools import wraps
from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from app.models import User, Article, Category, MediaLibrary, Comment

admin_bp = Blueprint("admin", __name__)


def admin_required(roles=("admin", "editor", "writer")):
    """Decorator for admin HTML pages – redirect to login on auth failure."""
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            try:
                verify_jwt_in_request(locations=["cookies"])
                identity = get_jwt_identity()
                user = User.query.get(int(identity))
                if not user or not user.is_active:
                    return redirect(url_for("auth.login_page"))
                if user.role not in roles:
                    return render_template("admin/403.html"), 403
            except Exception:
                return redirect(url_for("auth.login_page"))
            return fn(*args, **kwargs)
        return wrapper
    return decorator


def _get_current_admin():
    try:
        verify_jwt_in_request(locations=["cookies"])
        return User.query.get(int(get_jwt_identity()))
    except Exception:
        return None


# --------------------------------------------------------------------------- #
# Dashboard
# --------------------------------------------------------------------------- #
@admin_bp.route("/dashboard")
@admin_required()
def dashboard():
    user = _get_current_admin()
    total_articles = Article.query.count()
    published = Article.query.filter_by(status="published").count()
    drafts = Article.query.filter_by(status="draft").count()
    pending_comments = Comment.query.filter_by(is_approved=False).count()
    recent_articles = Article.query.order_by(Article.created_at.desc()).limit(8).all()
    categories = Category.query.order_by(Category.display_order.asc()).all()

    return render_template(
        "admin/dashboard.html",
        user=user,
        total_articles=total_articles,
        published=published,
        drafts=drafts,
        pending_comments=pending_comments,
        recent_articles=recent_articles,
        categories=categories,
    )


# --------------------------------------------------------------------------- #
# Articles
# --------------------------------------------------------------------------- #
@admin_bp.route("/articles")
@admin_required()
def articles():
    user = _get_current_admin()
    page = request.args.get("page", 1, type=int)
    status_filter = request.args.get("status", "")
    search_q = request.args.get("search", "")

    q = Article.query
    if user.role == "writer":
        q = q.filter_by(author_id=user.id)
    if status_filter:
        q = q.filter_by(status=status_filter)
    if search_q:
        q = q.filter(Article.title.ilike(f"%{search_q}%"))
    q = q.order_by(Article.created_at.desc())

    per_page = 20
    total = q.count()
    articles_list = q.offset((page - 1) * per_page).limit(per_page).all()
    pages = (total + per_page - 1) // per_page

    return render_template(
        "admin/articles.html",
        user=user,
        articles=articles_list,
        page=page,
        pages=pages,
        total=total,
        status_filter=status_filter,
        search_q=search_q,
    )


@admin_bp.route("/articles/new")
@admin_required()
def new_article():
    user = _get_current_admin()
    categories = Category.query.order_by(Category.name.asc()).all()
    return render_template("admin/article_form.html", user=user, categories=categories, article=None)


@admin_bp.route("/articles/<int:article_id>/edit")
@admin_required()
def edit_article(article_id):
    user = _get_current_admin()
    article = Article.query.get_or_404(article_id)
    if user.role == "writer" and article.author_id != user.id:
        return render_template("admin/403.html"), 403
    categories = Category.query.order_by(Category.name.asc()).all()
    return render_template("admin/article_form.html", user=user, categories=categories, article=article)


# --------------------------------------------------------------------------- #
# Categories
# --------------------------------------------------------------------------- #
@admin_bp.route("/categories")
@admin_required(roles=("admin", "editor"))
def categories():
    user = _get_current_admin()
    cats = Category.query.order_by(Category.display_order.asc(), Category.name.asc()).all()
    return render_template("admin/categories.html", user=user, categories=cats)


# --------------------------------------------------------------------------- #
# Users
# --------------------------------------------------------------------------- #
@admin_bp.route("/users")
@admin_required(roles=("admin",))
def users():
    user = _get_current_admin()
    all_users = User.query.order_by(User.created_at.desc()).all()
    return render_template("admin/users.html", user=user, all_users=all_users)


# --------------------------------------------------------------------------- #
# Media
# --------------------------------------------------------------------------- #
@admin_bp.route("/media")
@admin_required()
def media():
    user = _get_current_admin()
    page = request.args.get("page", 1, type=int)
    media_type = request.args.get("type", "")

    q = MediaLibrary.query
    if media_type:
        q = q.filter_by(media_type=media_type)
    q = q.order_by(MediaLibrary.uploaded_at.desc())

    per_page = 24
    total = q.count()
    media_list = q.offset((page - 1) * per_page).limit(per_page).all()
    pages = (total + per_page - 1) // per_page

    return render_template(
        "admin/media.html",
        user=user,
        media_list=media_list,
        page=page,
        pages=pages,
        total=total,
        media_type_filter=media_type,
    )


# --------------------------------------------------------------------------- #
# Comments
# --------------------------------------------------------------------------- #
@admin_bp.route("/comments")
@admin_required(roles=("admin", "editor"))
def comments():
    user = _get_current_admin()
    pending = Comment.query.filter_by(is_approved=False).order_by(Comment.created_at.desc()).all()
    approved = Comment.query.filter_by(is_approved=True).order_by(Comment.created_at.desc()).limit(20).all()
    return render_template("admin/comments.html", user=user, pending=pending, approved=approved)


# --------------------------------------------------------------------------- #
# Profile
# --------------------------------------------------------------------------- #
@admin_bp.route("/profile")
@admin_required()
def profile():
    user = _get_current_admin()
    return render_template("admin/profile.html", user=user)
