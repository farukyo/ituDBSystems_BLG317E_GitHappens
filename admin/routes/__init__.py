# Explicit imports instead of wildcard imports
from admin.routes import (
    home,
    people,
    movie,
    series,
    episode,
    ratings,
    genres,
    principals,
    professions,
    user,
    suggestion,
)

__all__ = [
    "home",
    "people",
    "movie",
    "series",
    "episode",
    "ratings",
    "genres",
    "principals",
    "professions",
    "user",
    "suggestion",
]
