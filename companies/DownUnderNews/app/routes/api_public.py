"""
Public JSON API – no authentication required.
Prefix: /api
"""
from flask import Blueprint, jsonify, request, render_template_string
from app.models import Article, Category, Tag
from app.utils import paginate_query
import subprocess
from sqlalchemy import text

api_public_bp = Blueprint("api_public", __name__)

DEFAULT_LIMIT = 10
MAX_LIMIT = 50


def _get_pagination():
    page = max(1, request.args.get("page", 1, type=int))
    limit = min(MAX_LIMIT, max(1, request.args.get("limit", DEFAULT_LIMIT, type=int)))
    return page, limit


# --------------------------------------------------------------------------- #
# Articles
# --------------------------------------------------------------------------- #
@api_public_bp.route("/articles")
def list_articles():
    page, limit = _get_pagination()
    category_slug = request.args.get("category", "")
    search_q = request.args.get("search", "").strip()

    q = Article.query.filter_by(status="published")

    if category_slug:
        cat = Category.query.filter_by(slug=category_slug).first()
        if cat:
            q = q.filter_by(category_id=cat.id)

    if search_q:
        q = q.filter(
            Article.title.ilike(f"%{search_q}%") | Article.content.ilike(f"%{search_q}%")
        )

    q = q.order_by(Article.published_at.desc())
    articles, total, pages = paginate_query(q, page, limit)

    return jsonify({
        "articles": [a.to_dict(include_content=False) for a in articles],
        "total": total,
        "page": page,
        "totalPages": pages,
    })


@api_public_bp.route("/articles/featured")
def featured_articles():
    articles = Article.query.filter_by(status="published", is_featured=True)\
        .order_by(Article.published_at.desc()).limit(10).all()
    return jsonify({"articles": [a.to_dict(include_content=False) for a in articles]})

# ! VULN: SSTI
@api_public_bp.route("/articles/<slug>")
def get_article(slug):
    article = Article.query.filter_by(slug=slug, status="published").first()
    if not article:
        html = f"<h1>404 - Page not found for {slug}."
        return render_template_string(html), 404

    related = []
    if article.category_id:
        related = Article.query.filter(
            Article.status == "published",
            Article.category_id == article.category_id,
            Article.id != article.id,
        ).order_by(Article.published_at.desc()).limit(4).all()

    return jsonify({
        "article": article.to_dict(),
        "related": [a.to_dict(include_content=False) for a in related],
    })


# --------------------------------------------------------------------------- #
# Categories
# --------------------------------------------------------------------------- #
@api_public_bp.route("/categories")
def list_categories():
    categories = Category.query.order_by(Category.display_order.asc(), Category.name.asc()).all()
    return jsonify({"categories": [c.to_dict() for c in categories]})


@api_public_bp.route("/categories/<slug>/articles")
def category_articles(slug):
    page, limit = _get_pagination()
    cat = Category.query.filter_by(slug=slug).first()

    q = Article.query.filter_by(status="published", category_id=cat.id)\
        .order_by(Article.published_at.desc())
    articles, total, pages = paginate_query(q, page, limit)
    return jsonify({
        "category": cat.to_dict(),
        "articles": [a.to_dict(include_content=False) for a in articles],
        "total": total,
        "page": page,
        "totalPages": pages,
    })


# --------------------------------------------------------------------------- #
# Search
# --------------------------------------------------------------------------- #
@api_public_bp.route("/search")
def search():
    page, limit = _get_pagination()
    q_str = request.args.get("q", "").strip()
    category_slug = request.args.get("category", "")
    author = request.args.get("author", "")
    date_from = request.args.get("date_from", "")
    date_to = request.args.get("date_to", "")

    if not q_str:
        return jsonify({"results": [], "total": 0, "query": ""})

    q = Article.query.filter(
        Article.status == "published",
        Article.title.ilike(f"%{q_str}%") | Article.content.ilike(f"%{q_str}%") | Article.excerpt.ilike(f"%{q_str}%"),
    )

    if category_slug:
        cat = Category.query.filter_by(slug=category_slug).first()
        if cat:
            q = q.filter_by(category_id=cat.id)

    if date_from:
        try:
            from datetime import datetime
            q = q.filter(Article.published_at >= datetime.fromisoformat(date_from))
        except ValueError:
            pass

    if date_to:
        try:
            from datetime import datetime
            q = q.filter(Article.published_at <= datetime.fromisoformat(date_to))
        except ValueError:
            pass

    q = q.order_by(Article.published_at.desc())
    results, total, pages = paginate_query(q, page, limit)

    return jsonify({
        "results": [a.to_dict(include_content=False) for a in results],
        "total": total,
        "query": q_str,
        "page": page,
        "totalPages": pages,
    })
