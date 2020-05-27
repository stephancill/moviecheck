from .auth import auth
from.explore import explore
from .watchlist import watchlist
from sanic import Blueprint

api = Blueprint.group(auth, explore, watchlist)