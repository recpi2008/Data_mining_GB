import datetime as dt
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from sqlalchemy import Column, Integer, String, ForeignKey, Table, DateTime, Boolean


Base = declarative_base() # декларируем базу

class UrlMixin:
    url = Column(String, nullable=False, unique=True)


class IdMixin:
    id = Column(Integer, primary_key=True, autoincrement=True)


class NameMixin:
    name = Column(String, nullable=False)


tag_post = Table(  # промежуточная таблица
    "tag_post",
    Base.metadata,
    Column("post_id", Integer, ForeignKey("post.id")),
    Column("tag_id", Integer, ForeignKey("tag.id")),
)


class Post(Base, UrlMixin):
    __tablename__ = "post" # название, иначе по дефолту возьмет из класса
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    author_id = Column(Integer, ForeignKey("author.id")) # многое к одному
    author = relationship("Author")
    tags = relationship("Tag", secondary=tag_post)
    comments = relationship("Comment")


class Author(Base, IdMixin, NameMixin, UrlMixin):
    __tablename__ = "author"
    posts = relationship("Post")


class Tag(Base, IdMixin, NameMixin, UrlMixin):
    __tablename__ = "tag"
    posts = relationship("Post", secondary=tag_post)


class Comment(Base):
    __tablename__ = "comment"
    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, ForeignKey("comment.id"), nullable=True)
    likes_count = Column(Integer)
    body = Column(String)
    created_at = Column(DateTime, nullable=False)
    hidden = Column(Boolean)
    deep = Column(Integer)
    author_id = Column(Integer, ForeignKey("author.id"))
    author = relationship("Author")
    time_now = Column(DateTime)
    post_id = Column(Integer, ForeignKey("post.id"))

    def __init__(self, **kwargs):
        self.id = kwargs["id"]
        self.parent_id = kwargs["parent_id"]
        self.likes_count = kwargs["likes_count"]
        self.body = kwargs["body"]
        self.created_at = dt.datetime.fromisoformat(kwargs["created_at"])
        self.hidden = kwargs["hidden"]
        self.deep = kwargs["deep"]
        self.time_now = dt.datetime.fromisoformat(kwargs["time_now"])
        self.author = kwargs["author"]