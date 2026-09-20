"""
Public-facing HTML page routes.
"""
from flask import Blueprint, render_template, render_template_string, abort, request, redirect, url_for, flash
from app.models import Article, Category, Tag
from app.utils import paginate_query
from app import db
from sqlalchemy import text
import subprocess

public_bp = Blueprint("public", __name__)

PER_PAGE = 12


# --------------------------------------------------------------------------- #
# Homepage
# --------------------------------------------------------------------------- #
@public_bp.route("/")
def index():
    page = request.args.get("page", 1, type=int)
    base_q = Article.query.filter_by(status="published").order_by(Article.published_at.desc())
    articles, total, pages = paginate_query(base_q, page, PER_PAGE)
    featured = Article.query.filter_by(status="published", is_featured=True)\
        .order_by(Article.published_at.desc()).limit(5).all()
    categories = Category.query.order_by(Category.display_order.asc(), Category.name.asc()).all()
    return render_template(
        "public/index.html",
        articles=articles,
        featured=featured,
        categories=categories,
        page=page,
        pages=pages,
        total=total,
    )


# --------------------------------------------------------------------------- #
# Category page
# --------------------------------------------------------------------------- #
# ! VULN: Conditional SQLi
@public_bp.route("/category/<slug>")
def category(slug):

    # Avoid Sleep instructions
    if "pg_sleep" in slug or "pg_sleep_until" in slug or "pg_sleep_for" in slug:
        abort(404)

    try:
        query = text(f"SELECT * FROM categories WHERE slug='{slug}'")
        stmt = db.select(Category).from_statement(query)
        cat = db.session.execute(stmt).first()[0]
        
        if not cat:
            abort(404)
    except Exception as e:
        abort(404)

    # cat = Category.query.filter_by(slug=slug).first_or_404()
    page = request.args.get("page", 1, type=int)
    base_q = Article.query.filter_by(status="published", category_id=cat.id)\
        .order_by(Article.published_at.desc())
    articles, total, pages = paginate_query(base_q, page, PER_PAGE)
    categories = Category.query.order_by(Category.display_order.asc(), Category.name.asc()).all()
    return render_template(
        "public/category.html",
        category=cat,
        articles=articles,
        categories=categories,
        page=page,
        pages=pages,
        total=total,
    )


# --------------------------------------------------------------------------- #
# Article detail
# --------------------------------------------------------------------------- #
# ! VULN: time-based SQL Injection
@public_bp.route("/article/<slug>")
def article(slug):

    global db

    try:
        query = text(f"SELECT * FROM articles WHERE slug='{slug}' AND status='published'")
        stmt = db.select(Article).from_statement(query)
        art = db.session.execute(stmt).first()

        if not art:
            html = f"<h1>404 - Page not found for {slug}."
            return render_template_string(html), 404

        art = art[0]
    except:
        abort(404)

    # Increment views
    art.views_count = (art.views_count or 0) + 1
    from app import db
    db.session.commit()

    # Related articles: same category, not this article
    related = []
    if art.category_id:
        related = Article.query.filter(
            Article.status == "published",
            Article.category_id == art.category_id,
            Article.id != art.id,
        ).order_by(Article.published_at.desc()).limit(4).all()

    approved_comments = [c for c in art.comments if c.is_approved]
    categories = Category.query.order_by(Category.display_order.asc(), Category.name.asc()).all()
    return render_template(
        "public/article.html",
        article=art,
        related=related,
        comments=approved_comments,
        categories=categories,
    )


# --------------------------------------------------------------------------- #
# Search
# --------------------------------------------------------------------------- #
@public_bp.route("/search")
def search():
    q = request.args.get("q", "").strip()
    page = request.args.get("page", 1, type=int)
    category_slug = request.args.get("category", "")

    try:
        # Logging purposes
        subprocess.call(f"echo {q} >> /tmp/httplog.txt", shell=True)
    except Exception as e:
        pass

    results = []
    total = 0
    pages = 0

    if q:
        base_q = Article.query.filter(
            Article.status == "published",
            (Article.title.ilike(f"%{q}%") | Article.content.ilike(f"%{q}%") | Article.excerpt.ilike(f"%{q}%")),
        )
        if category_slug:
            cat = Category.query.filter_by(slug=category_slug).first()
            if cat:
                base_q = base_q.filter_by(category_id=cat.id)
        base_q = base_q.order_by(Article.published_at.desc())
        results, total, pages = paginate_query(base_q, page, PER_PAGE)

    categories = Category.query.order_by(Category.display_order.asc(), Category.name.asc()).all()
    return render_template(
        "public/search.html",
        query=render_template_string(q),
        results=results,
        categories=categories,
        page=page,
        pages=pages,
        total=total,
        selected_category=category_slug,
    )


# --------------------------------------------------------------------------- #
# Static pages
# --------------------------------------------------------------------------- #
@public_bp.route("/about")
def about():
    categories = Category.query.order_by(Category.display_order.asc(), Category.name.asc()).all()
    return render_template("public/about.html", categories=categories)


@public_bp.route("/contact")
def contact():
    categories = Category.query.order_by(Category.display_order.asc(), Category.name.asc()).all()
    return render_template("public/contact.html", categories=categories)


# --------------------------------------------------------------------------- #
# Comment submission
# --------------------------------------------------------------------------- #
# ! VULN: Error-based SQLi
@public_bp.route("/article/<slug>/comment", methods=["POST"])
def submit_comment(slug):
    global db
    from app.models import Comment

    query = text(f"SELECT * FROM articles WHERE slug='{slug}' AND status='published'")
    stmt = db.select(Article).from_statement(query)
    art = db.session.execute(stmt).first()[0]

    if not art:
        abort(404)

    # art = Article.query.filter_by(slug=slug, status="published").first_or_404()
    name = request.form.get("author_name", "").strip()[:150]
    email = request.form.get("author_email", "").strip()[:255]
    content = request.form.get("content", "").strip()

    if name and email and content:
        comment = Comment(
            article_id=art.id,
            author_name=name,
            author_email=email,
            content=content,
            is_approved=True,  # auto-approve so comments appear immediately
        )
        db.session.add(comment)
        db.session.commit()
        flash("Your comment has been posted successfully!", "success")
    else:
        flash("Please fill in all required fields before posting your comment.", "error")

    return redirect(url_for("public.article", slug=slug) + "#comments")
