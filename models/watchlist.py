from pony.orm import *
from .user import db, User
from .movie_item import MovieItem

class Watchlist(db.Entity):
    id = PrimaryKey(int, auto=True)
    is_default = Optional(bool)
    title = Optional(str)
    movie_items = Set(MovieItem)
    user = Required(User)
