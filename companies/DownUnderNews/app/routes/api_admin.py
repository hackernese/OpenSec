"""
Admin JSON API – authentication required via JWT.
Prefix: /api/admin
"""
from datetime import datetime, timezone
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity

from app import db, bcrypt
from app.models import Article, Category, Tag, User, ArticleMedia, MediaLibrary, Comment
from app.utils import (
    slugify, unique_slug, paginate_query,
    get_current_user, jwt_required_with_role,
    upload_to_media_server, delete_from_media_server,
    validate_file_upload, error, success,
)
from sqlalchemy import text

api_admin_bp = Blueprint("api_admin", __name__)

# =========================================================================== #
# Authentication
# =========================================================================== #
# ! VULN: Error-based SQLi
@api_admin_bp.route("/login", methods=["POST"])
def api_login():
    from app import bcrypt
    from flask_jwt_extended import create_access_token
    from flask import make_response
    from flask_jwt_extended import set_access_cookies

    data = request.get_json() or {}
    identifier = data.get("username") or data.get("email", "")
    password = data.get("password", "")

    if not identifier or not password:
        return error("Username and password required")

    query = text(f"SELECT * FROM users WHERE username='{identifier}' OR email='{identifier}'")
    stmt = db.select(User).from_statement(query)
    art = db.session.execute(stmt).first()[0]

    # user = User.query.filter(
    #     (User.username == identifier) | (User.email == identifier)
    # ).first()

    if not user or not bcrypt.check_password_hash(user.password_hash, password):
        return error("Invalid credentials", 401)

    if not user.is_active:
        return error("Account is deactivated", 403)

    token = create_access_token(identity=str(user.id))
    return jsonify({"token": token, "user": user.to_dict()})


@api_admin_bp.route("/me", methods=["GET"])
@jwt_required(locations=["headers", "cookies"])
def me():
    user = get_current_user()
    if not user:
        return error("User not found", 404)
    return jsonify({"user": user.to_dict()})


# =========================================================================== #
# Articles
# =========================================================================== #
@api_admin_bp.route("/articles", methods=["GET"])
@jwt_required_with_role("admin", "editor", "writer")
def list_articles():
    page = max(1, request.args.get("page", 1, type=int))
    limit = min(50, request.args.get("limit", 20, type=int))
    status_filter = request.args.get("status", "")
    category_id = request.args.get("category", type=int)
    search_q = request.args.get("search", "").strip()

    user = get_current_user()
    q = Article.query

    # Writers can only see their own articles
    if user.role == "writer":
        q = q.filter_by(author_id=user.id)

    if status_filter:
        q = q.filter_by(status=status_filter)
    if category_id:
        q = q.filter_by(category_id=category_id)
    if search_q:
        q = q.filter(Article.title.ilike(f"%{search_q}%"))

    q = q.order_by(Article.created_at.desc())
    articles, total, pages = paginate_query(q, page, limit)

    return jsonify({
        "articles": [a.to_dict(include_content=False) for a in articles],
        "total": total,
        "page": page,
        "totalPages": pages,
    })


@api_admin_bp.route("/articles/<int:article_id>", methods=["GET"])
@jwt_required_with_role("admin", "editor", "writer")
def get_article(article_id):
    user = get_current_user()
    article = Article.query.get_or_404(article_id)
    if user.role == "writer" and article.author_id != user.id:
        return error("Access denied", 403)
    return jsonify({"article": article.to_dict()})


@api_admin_bp.route("/articles", methods=["POST"])
@jwt_required_with_role("admin", "editor", "writer")
def create_article():
    user = get_current_user()
    data = request.get_json() or {}

    title = data.get("title", "").strip()
    if not title:
        return error("Title is required")

    content = data.get("content", "").strip()
    if not content:
        return error("Content is required")

    base_slug = slugify(title)
    slug = unique_slug(base_slug, Article)

    # Determine status
    status = data.get("status", "draft")
    if user.role == "writer":
        status = "draft"  # writers must stay in draft

    published_at = None
    if status == "published":
        published_at = datetime.now(timezone.utc)
        if data.get("published_at"):
            try:
                published_at = datetime.fromisoformat(data["published_at"])
            except ValueError:
                pass

    # Tags
    tag_names = [t.strip() for t in data.get("tags", []) if isinstance(t, str)]
    tags = []
    for tag_name in tag_names:
        tag_slug = slugify(tag_name)
        tag = Tag.query.filter_by(slug=tag_slug).first()
        if not tag:
            tag = Tag(name=tag_name, slug=tag_slug)
            db.session.add(tag)
        tags.append(tag)

    article = Article(
        title=title,
        slug=slug,
        subtitle=data.get("subtitle", "").strip() or None,
        content=content,
        excerpt=data.get("excerpt", "").strip() or None,
        author_id=user.id,
        category_id=data.get("category_id"),
        featured_image_url=data.get("featured_image_url"),
        status=status,
        published_at=published_at,
        is_featured=data.get("is_featured", False),
        tags=tags,
    )
    db.session.add(article)
    db.session.commit()
    return jsonify({"article": article.to_dict()}), 201


@api_admin_bp.route("/articles/<int:article_id>", methods=["PUT"])
@jwt_required_with_role("admin", "editor", "writer")
def update_article(article_id):
    user = get_current_user()
    article = Article.query.get_or_404(article_id)

    if user.role == "writer" and article.author_id != user.id:
        return error("Access denied", 403)

    data = request.get_json() or {}

    if "title" in data and data["title"].strip():
        new_title = data["title"].strip()
        if new_title != article.title:
            article.title = new_title
            article.slug = unique_slug(slugify(new_title), Article, existing_id=article.id)

    if "content" in data:
        article.content = data["content"]
    if "subtitle" in data:
        article.subtitle = data["subtitle"]
    if "excerpt" in data:
        article.excerpt = data["excerpt"]
    if "category_id" in data:
        article.category_id = data["category_id"]
    if "featured_image_url" in data:
        article.featured_image_url = data["featured_image_url"]
    if "is_featured" in data and user.role in ("admin", "editor"):
        article.is_featured = bool(data["is_featured"])

    # Status transitions
    if "status" in data and user.role != "writer":
        new_status = data["status"]
        if new_status in ("draft", "published", "archived"):
            if new_status == "published" and article.status != "published":
                article.published_at = article.published_at or datetime.now(timezone.utc)
            article.status = new_status

    # Tags
    if "tags" in data:
        tag_names = [t.strip() for t in data["tags"] if isinstance(t, str)]
        tags = []
        for tag_name in tag_names:
            tag_slug = slugify(tag_name)
            tag = Tag.query.filter_by(slug=tag_slug).first()
            if not tag:
                tag = Tag(name=tag_name, slug=tag_slug)
                db.session.add(tag)
            tags.append(tag)
        article.tags = tags

    article.updated_at = datetime.now(timezone.utc)
    db.session.commit()
    return jsonify({"article": article.to_dict()})


# ! VULN: IDOR - Writer isn't supposed to be deleting any post
@api_admin_bp.route("/articles/<int:article_id>", methods=["DELETE"])
@jwt_required_with_role("admin", "editor", "writer")
def delete_article(article_id):
    article = Article.query.get_or_404(article_id)
    db.session.delete(article)
    db.session.commit()
    return success(message="Article deleted")


@api_admin_bp.route("/articles/<int:article_id>/publish", methods=["PATCH"])
@jwt_required_with_role("admin", "editor")
def publish_article(article_id):
    article = Article.query.get_or_404(article_id)
    article.status = "published"
    article.published_at = article.published_at or datetime.now(timezone.utc)
    article.updated_at = datetime.now(timezone.utc)
    db.session.commit()
    return jsonify({"article": article.to_dict()})


@api_admin_bp.route("/articles/<int:article_id>/unpublish", methods=["PATCH"])
@jwt_required_with_role("admin", "editor")
def unpublish_article(article_id):
    article = Article.query.get_or_404(article_id)
    article.status = "draft"
    article.updated_at = datetime.now(timezone.utc)
    db.session.commit()
    return jsonify({"article": article.to_dict()})


# =========================================================================== #
# Categories
# =========================================================================== #
@api_admin_bp.route("/categories", methods=["GET"])
@jwt_required_with_role("admin", "editor", "writer")
def list_categories():
    categories = Category.query.order_by(Category.display_order.asc(), Category.name.asc()).all()
    return jsonify({"categories": [c.to_dict() for c in categories]})


@api_admin_bp.route("/categories", methods=["POST"])
@jwt_required_with_role("admin", "editor")
def create_category():
    data = request.get_json() or {}
    name = data.get("name", "").strip()
    if not name:
        return error("Category name is required")

    base_slug = data.get("slug", "").strip() or slugify(name)
    slug = unique_slug(base_slug, Category)

    cat = Category(
        name=name,
        slug=slug,
        description=data.get("description", ""),
        display_order=data.get("display_order", 0),
    )
    db.session.add(cat)
    db.session.commit()
    return jsonify({"category": cat.to_dict()}), 201


@api_admin_bp.route("/categories/<int:cat_id>", methods=["PUT"])
@jwt_required_with_role("admin", "editor")
def update_category(cat_id):
    cat = Category.query.get_or_404(cat_id)
    data = request.get_json() or {}

    if "name" in data:
        cat.name = data["name"].strip()
    if "slug" in data:
        new_slug = data["slug"].strip() or slugify(cat.name)
        cat.slug = unique_slug(new_slug, Category, existing_id=cat_id)
    if "description" in data:
        cat.description = data["description"]
    if "display_order" in data:
        cat.display_order = int(data["display_order"])

    db.session.commit()
    return jsonify({"category": cat.to_dict()})


@api_admin_bp.route("/categories/<int:cat_id>", methods=["DELETE"])
@jwt_required_with_role("admin")
def delete_category(cat_id):
    cat = Category.query.get_or_404(cat_id)
    db.session.delete(cat)
    db.session.commit()
    return success(message="Category deleted")


# =========================================================================== #
# Users  (admin only)
# =========================================================================== #
@api_admin_bp.route("/users", methods=["GET"])
@jwt_required_with_role("admin")
def list_users():
    users = User.query.order_by(User.created_at.desc()).all()
    return jsonify({"users": [u.to_dict() for u in users]})


@api_admin_bp.route("/users", methods=["POST"])
@jwt_required_with_role("admin")
def create_user():
    data = request.get_json() or {}
    username = data.get("username", "").strip()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")
    role = data.get("role", "writer")

    if not username or not email or not password:
        return error("username, email and password are required")
    if role not in ("admin", "editor", "writer"):
        return error("Invalid role")
    if len(password) < 8:
        return error("Password must be at least 8 characters")

    if User.query.filter_by(username=username).first():
        return error("Username already taken", 409)
    if User.query.filter_by(email=email).first():
        return error("Email already in use", 409)

    user = User(
        username=username,
        email=email,
        password_hash=bcrypt.generate_password_hash(password).decode("utf-8"),
        role=role,
        first_name=data.get("first_name", ""),
        last_name=data.get("last_name", ""),
        is_active=True,
    )
    db.session.add(user)
    db.session.commit()
    return jsonify({"user": user.to_dict()}), 201


@api_admin_bp.route("/users/<int:user_id>", methods=["PUT"])
@jwt_required_with_role("admin")
def update_user(user_id):
    user = User.query.get_or_404(user_id)
    data = request.get_json() or {}

    if "email" in data:
        email = data["email"].strip().lower()
        if User.query.filter(User.email == email, User.id != user_id).first():
            return error("Email already in use", 409)
        user.email = email
    if "role" in data:
        if data["role"] not in ("admin", "editor", "writer"):
            return error("Invalid role")
        user.role = data["role"]
    if "first_name" in data:
        user.first_name = data["first_name"]
    if "last_name" in data:
        user.last_name = data["last_name"]
    if "is_active" in data:
        user.is_active = bool(data["is_active"])

    user.updated_at = datetime.now(timezone.utc)
    db.session.commit()
    return jsonify({"user": user.to_dict()})


@api_admin_bp.route("/users/<int:user_id>", methods=["DELETE"])
@jwt_required_with_role("admin")
def delete_user(user_id):
    current = get_current_user()
    if current.id == user_id:
        return error("Cannot delete your own account", 400)
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return success(message="User deleted")


@api_admin_bp.route("/users/<int:user_id>/reset-password", methods=["POST"])
@jwt_required_with_role("admin")
def reset_user_password(user_id):
    user = User.query.get_or_404(user_id)
    data = request.get_json() or {}
    new_password = data.get("new_password", "")
    if len(new_password) < 8:
        return error("Password must be at least 8 characters")
    user.password_hash = bcrypt.generate_password_hash(new_password).decode("utf-8")
    user.updated_at = datetime.now(timezone.utc)
    db.session.commit()
    return success(message="Password reset successfully")


# =========================================================================== #
# Media upload & library
# =========================================================================== #
@api_admin_bp.route("/media/upload", methods=["POST"])
@jwt_required_with_role("admin", "editor", "writer")
def upload_media():
    user = get_current_user()

    if "file" not in request.files:
        return error("No file provided")

    file = request.files["file"]
    if not file.filename:
        return error("No file selected")

    is_valid, err_msg, media_type = validate_file_upload(file)
    if not is_valid:
        return error(err_msg)

    try:
        result = upload_to_media_server(file.stream, file.filename, file.content_type)
    except Exception as exc:
        return error(f"Upload failed: {str(exc)}", 502)

    # Save to media library
    entry = MediaLibrary(
        file_name=result["filename"],
        original_name=result["original_name"],
        media_url=result["url"],
        media_type=media_type,
        file_size=result.get("size", 0),
        uploaded_by=user.id,
    )
    db.session.add(entry)
    db.session.commit()

    return jsonify({
        "url": result["url"],
        "filename": result["filename"],
        "size": result.get("size", 0),
        "media": entry.to_dict(),
    }), 201


@api_admin_bp.route("/media", methods=["GET"])
@jwt_required_with_role("admin", "editor", "writer")
def list_media():
    page = max(1, request.args.get("page", 1, type=int))
    limit = min(50, request.args.get("limit", 20, type=int))
    media_type = request.args.get("type", "")

    q = MediaLibrary.query
    if media_type:
        q = q.filter_by(media_type=media_type)
    q = q.order_by(MediaLibrary.uploaded_at.desc())

    items, total, pages = paginate_query(q, page, limit)
    return jsonify({
        "media": [m.to_dict() for m in items],
        "total": total,
        "page": page,
        "totalPages": pages,
    })


@api_admin_bp.route("/media/<int:media_id>", methods=["DELETE"])
@jwt_required_with_role("admin", "editor")
def delete_media(media_id):
    entry = MediaLibrary.query.get_or_404(media_id)
    delete_from_media_server(entry.file_name)
    db.session.delete(entry)
    db.session.commit()
    return success(message="Media deleted")


# =========================================================================== #
# Dashboard stats
# =========================================================================== #
@api_admin_bp.route("/dashboard", methods=["GET"])
@jwt_required_with_role("admin", "editor", "writer")
def dashboard_stats():
    total_articles = Article.query.count()
    published = Article.query.filter_by(status="published").count()
    drafts = Article.query.filter_by(status="draft").count()
    total_categories = Category.query.count()
    total_users = User.query.count()
    pending_comments = Comment.query.filter_by(is_approved=False).count()
    total_media = MediaLibrary.query.count()

    recent_articles = Article.query.order_by(Article.created_at.desc()).limit(5).all()
    popular_articles = Article.query.filter_by(status="published")\
        .order_by(Article.views_count.desc()).limit(5).all()

    return jsonify({
        "stats": {
            "total_articles": total_articles,
            "published_articles": published,
            "draft_articles": drafts,
            "total_categories": total_categories,
            "total_users": total_users,
            "pending_comments": pending_comments,
            "total_media": total_media,
        },
        "recent_articles": [a.to_dict(include_content=False) for a in recent_articles],
        "popular_articles": [a.to_dict(include_content=False) for a in popular_articles],
    })


# =========================================================================== #
# Comments moderation
# =========================================================================== #
@api_admin_bp.route("/comments", methods=["GET"])
@jwt_required_with_role("admin", "editor")
def list_comments():
    page = max(1, request.args.get("page", 1, type=int))
    limit = min(50, request.args.get("limit", 20, type=int))
    approved_filter = request.args.get("approved", "")

    q = Comment.query
    if approved_filter == "pending":
        q = q.filter_by(is_approved=False)
    elif approved_filter == "approved":
        q = q.filter_by(is_approved=True)

    q = q.order_by(Comment.created_at.desc())
    items, total, pages = paginate_query(q, page, limit)

    return jsonify({
        "comments": [
            {**c.to_dict(), "author_email": c.author_email, "is_approved": c.is_approved}
            for c in items
        ],
        "total": total,
        "page": page,
        "totalPages": pages,
    })


@api_admin_bp.route("/comments/<int:comment_id>/approve", methods=["PATCH"])
@jwt_required_with_role("admin", "editor")
def approve_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    comment.is_approved = True
    db.session.commit()
    return success(message="Comment approved")


@api_admin_bp.route("/comments/<int:comment_id>", methods=["DELETE"])
@jwt_required_with_role("admin", "editor")
def delete_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    db.session.delete(comment)
    db.session.commit()
    return success(message="Comment deleted")
