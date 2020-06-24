from datetime import datetime
from pony.orm import *
from .user import db, User

class MovieItem(db.Entity):
    id = PrimaryKey(int, auto=True)
    imdb_id = Optional(str)
    date = Optional(datetime)
    user = Optional(User)
    watchlist = Optional('Watchlist')
    rating = Optional(int)
