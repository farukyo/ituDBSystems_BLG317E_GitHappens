from database.db import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

# --- ASSOCIATION TABLES FOR LIKES ---
# These tables don't need a class. They just link two other tables.

user_liked_movies = db.Table(
    "user_liked_movies",
    db.Column("user_id", db.Integer, db.ForeignKey("users.id"), primary_key=True),
    db.Column("movie_id", db.Integer, db.ForeignKey("movies.id"), primary_key=True),
)

user_liked_series = db.Table(
    "user_liked_series",
    db.Column("user_id", db.Integer, db.ForeignKey("users.id"), primary_key=True),
    db.Column("series_id", db.Integer, db.ForeignKey("series.id"), primary_key=True),
)

user_liked_actors = db.Table(
    "user_liked_actors",
    db.Column("user_id", db.Integer, db.ForeignKey("users.id"), primary_key=True),
    db.Column("actor_id", db.Integer, db.ForeignKey("actors.id"), primary_key=True),
)


# --- YOUR MODELS ---


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)

    # 1. ADDED QUIZ SCORE
    score = db.Column(db.Integer, nullable=True, default=0)

    # 2. ADDED RELATIONSHIPS FOR LIKES
    liked_movies = db.relationship(
        "Movie",
        secondary=user_liked_movies,
        lazy="subquery",
        backref=db.backref("liked_by_users", lazy=True),
    )

    liked_series = db.relationship(
        "Series",
        secondary=user_liked_series,
        lazy="subquery",
        backref=db.backref("liked_by_users", lazy=True),
    )

    liked_actors = db.relationship(
        "Actor",
        secondary=user_liked_actors,
        lazy="subquery",
        backref=db.backref("liked_by_users", lazy=True),
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password, method="pbkdf2:sha256")

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.username}>"


# --- PLACEHOLDER MODELS ---
# You must have these models for the relationships to work.
# Your actual models from the IMDb data will be more complex.


class Movie(db.Model):
    __tablename__ = "movies"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    # ... other columns like year, rating, etc.


class Series(db.Model):
    __tablename__ = "series"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    # ... other columns


class Actor(db.Model):
    __tablename__ = "actors"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    # ... other columns
