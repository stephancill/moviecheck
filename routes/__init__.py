from .auth import auth
from .explore import explore
from .import_external import  import_external
from .watchlist import watchlist
from sanic import Blueprint

api = Blueprint.group(auth, explore, import_external, watchlist)