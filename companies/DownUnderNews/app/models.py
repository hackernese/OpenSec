from datetime import datetime, timezone
from app import db


# --------------------------------------------------------------------------- #
# Junction table: articles <-> tags
# --------------------------------------------------------------------------- #
article_tags = db.Table(
    "article_tags",
    db.Column("article_id", db.Integer, db.ForeignKey("articles.id", ondelete="CASCADE"), primary_key=True),
    db.Column("tag_id", db.Integer, db.ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
)


# --------------------------------------------------------------------------- #
# Users
# --------------------------------------------------------------------------- #
class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.Enum("admin", "editor", "writer", name="user_role"), nullable=False, default="writer")
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    articles = db.relationship("Article", back_populates="author", lazy="dynamic")

    def to_dict(self, include_sensitive=False):
        data = {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "role": self.role,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
        return data

    @property
    def full_name(self):
        parts = [p for p in [self.first_name, self.last_name] if p]
        return " ".join(parts) if parts else self.username


# --------------------------------------------------------------------------- #
# Categories
# --------------------------------------------------------------------------- #
class Category(db.Model):
    __tablename__ = "categories"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    slug = db.Column(db.String(120), unique=True, nullable=False)
    description = db.Column(db.Text)
    display_order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    articles = db.relationship("Article", back_populates="category", lazy="dynamic")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "slug": self.slug,
            "description": self.description,
            "display_order": self.display_order,
            "article_count": self.articles.filter_by(status="published").count(),
        }


# --------------------------------------------------------------------------- #
# Articles
# --------------------------------------------------------------------------- #
class Article(db.Model):
    __tablename__ = "articles"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(500), nullable=False)
    slug = db.Column(db.String(600), unique=True, nullable=False)
    subtitle = db.Column(db.String(500))
    content = db.Column(db.Text, nullable=False)
    excerpt = db.Column(db.Text)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id", ondelete="SET NULL"), nullable=True)
    featured_image_url = db.Column(db.String(1024))
    status = db.Column(
        db.Enum("draft", "published", "archived", name="article_status"),
        nullable=False,
        default="draft",
    )
    published_at = db.Column(db.DateTime(timezone=True))
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
    views_count = db.Column(db.Integer, default=0)
    is_featured = db.Column(db.Boolean, default=False)

    author = db.relationship("User", back_populates="articles")
    category = db.relationship("Category", back_populates="articles")
    media = db.relationship("ArticleMedia", back_populates="article", cascade="all, delete-orphan")
    comments = db.relationship("Comment", back_populates="article", cascade="all, delete-orphan")
    tags = db.relationship("Tag", secondary=article_tags, back_populates="articles", lazy="subquery")

    def to_dict(self, include_content=True):
        data = {
            "id": self.id,
            "title": self.title,
            "slug": self.slug,
            "subtitle": self.subtitle,
            "excerpt": self.excerpt,
            "author": self.author.to_dict() if self.author else None,
            "category": self.category.to_dict() if self.category else None,
            "featured_image_url": self.featured_image_url,
            "status": self.status,
            "published_at": self.published_at.isoformat() if self.published_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "views_count": self.views_count,
            "is_featured": self.is_featured,
            "tags": [t.to_dict() for t in self.tags],
            "media": [m.to_dict() for m in self.media],
        }
        if include_content:
            data["content"] = self.content
        return data


# --------------------------------------------------------------------------- #
# Article Media
# --------------------------------------------------------------------------- #
class ArticleMedia(db.Model):
    __tablename__ = "article_media"

    id = db.Column(db.Integer, primary_key=True)
    article_id = db.Column(db.Integer, db.ForeignKey("articles.id", ondelete="CASCADE"), nullable=False)
    media_url = db.Column(db.String(1024), nullable=False)
    media_type = db.Column(db.Enum("image", "document", "pdf", name="media_type_enum"), nullable=False)
    file_name = db.Column(db.String(255))
    file_size = db.Column(db.Integer)
    display_order = db.Column(db.Integer, default=0)
    caption = db.Column(db.Text)
    uploaded_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    article = db.relationship("Article", back_populates="media")

    def to_dict(self):
        return {
            "id": self.id,
            "article_id": self.article_id,
            "media_url": self.media_url,
            "media_type": self.media_type,
            "file_name": self.file_name,
            "file_size": self.file_size,
            "display_order": self.display_order,
            "caption": self.caption,
            "uploaded_at": self.uploaded_at.isoformat() if self.uploaded_at else None,
        }


# --------------------------------------------------------------------------- #
# Tags
# --------------------------------------------------------------------------- #
class Tag(db.Model):
    __tablename__ = "tags"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    slug = db.Column(db.String(120), unique=True, nullable=False)

    articles = db.relationship("Article", secondary=article_tags, back_populates="tags", lazy="dynamic")

    def to_dict(self):
        return {"id": self.id, "name": self.name, "slug": self.slug}


# --------------------------------------------------------------------------- #
# Comments
# --------------------------------------------------------------------------- #
class Comment(db.Model):
    __tablename__ = "comments"

    id = db.Column(db.Integer, primary_key=True)
    article_id = db.Column(db.Integer, db.ForeignKey("articles.id", ondelete="CASCADE"), nullable=False)
    author_name = db.Column(db.String(150), nullable=False)
    author_email = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    is_approved = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    article = db.relationship("Article", back_populates="comments")

    def to_dict(self):
        return {
            "id": self.id,
            "article_id": self.article_id,
            "author_name": self.author_name,
            "content": self.content,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


# --------------------------------------------------------------------------- #
# Media Library (standalone, not tied to a specific article)
# --------------------------------------------------------------------------- #
class MediaLibrary(db.Model):
    __tablename__ = "media_library"

    id = db.Column(db.Integer, primary_key=True)
    file_name = db.Column(db.String(255), nullable=False)
    original_name = db.Column(db.String(255))
    media_url = db.Column(db.String(1024), nullable=False)
    media_type = db.Column(db.Enum("image", "document", "pdf", name="library_media_type"), nullable=False)
    file_size = db.Column(db.Integer)
    uploaded_by = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    uploaded_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    uploader = db.relationship("User")

    def to_dict(self):
        return {
            "id": self.id,
            "file_name": self.file_name,
            "original_name": self.original_name,
            "media_url": self.media_url,
            "media_type": self.media_type,
            "file_size": self.file_size,
            "uploaded_by": self.uploader.username if self.uploader else None,
            "uploaded_at": self.uploaded_at.isoformat() if self.uploaded_at else None,
        }
